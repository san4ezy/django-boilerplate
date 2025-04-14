import os
import shutil
import string
import secrets
import base64

from fabric import task
from pathlib import Path


class Core:
    @staticmethod
    def load_dotenv(filepath=".env"):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Env file not found: {filepath}")

        with open(filepath, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    key, value = key.strip(), value.strip().strip('"').strip("'")
                    os.environ[key] = value

    @staticmethod
    def generate_secret(
            l: int = 32,
            is_letters: bool = True,
            is_digits: bool = True,
            is_special_chars: bool = True,
    ):
        chars = ""
        if is_digits:
            chars += string.digits
        if is_letters:
            chars += string.ascii_letters
        if is_special_chars:
            chars += "!@#$%^&*()"
        return "".join(
            secrets.choice(chars) for _ in range(l)
        )

    @staticmethod
    def generate_fernet():
        key = os.urandom(32)
        fernet_key = base64.urlsafe_b64encode(key)
        return fernet_key.decode()


class S:
    @staticmethod
    def p(s, color: str, style: str):
        s = str(s)
        fs = {
            "normal": 0,
            "blind": 2,
            "italic": 3,
            "underline": 4,
            "highlighted": 7,
        }[style]
        fc = {
            "black": 30,
            "red": 91,
            "green": 92,
            "yellow": 93,
            "blue": 94,
            "purple": 95,
            "cyan": 96,
            "grey": 37,
            "white": 97,
        }[color]
        return f"\x1b[{fs};{fc}m{s}\x1b[0m"

    @classmethod
    def normal(cls, s):
        return cls.p(s, color="white", style="normal")

    @classmethod
    def warning(cls, s):
        return cls.p(s, color="yellow", style="normal")

    @classmethod
    def danger(cls, s):
        return cls.p(s, color="red", style="normal")

    @classmethod
    def success(cls, s):
        return cls.p(s, color="green", style="normal")

    @classmethod
    def info(cls, s):
        return cls.p(s, color="blue", style="normal")

    @classmethod
    def secondary(cls, s):
        return cls.p(s, color="blue", style="blind")

    @classmethod
    def highlighted(cls, s):
        return cls.p(s, color="yellow", style="highlighted")


Core.load_dotenv(".env")

ENV = os.getenv("ENV", "development")
PROJECT_NAME = os.getenv("PROJECT_NAME")
APP_NAME = os.getenv("APP_NAME")
APP_PORT = os.getenv("APP_PORT")
COMPOSE = Path("environments") / ENV / "docker-compose.yml"
ENV_FILE = Path("environments") / ENV / "app.env"

TEST_MODE: bool = False


class InstallTasks:
    def setup(self, c):
        env_dir = Path("environments") / ENV

        print(S.info("Env directory"), S.normal(env_dir))
        filenames = (
            ("app.env.example", "app.env",),
            ("docker-compose.yml.example", "docker-compose.yml",),
        )
        for src, dst in filenames:
            print(f"Copying {env_dir / dst} ...", end="")
            shutil.copy(env_dir / src, env_dir / dst)
            print(S.success(" [OK]"))

        replaces = {
            "PROJECT_NAME": PROJECT_NAME,
            "APP_NAME": APP_NAME,
            "APP_PORT": APP_PORT,
        }

        with open(COMPOSE) as f:
            content = f.read()

        for key, value in replaces.items():
            content = content.replace(f'<{key}>', value)

        with open(COMPOSE, "w") as f:
            f.write(content)

        print(S.success("Env copied."))
        print(S.warning("!IMPORTANT! Replace the standard keys with your own and keep it safe!!!"))

    def keygen(self, c):
        replaces = {
            "POSTGRES_PASSWORD": Core.generate_secret(16, is_special_chars=False),
            "SECRET_KEY": Core.generate_secret(50),
            "JWT_SIGNING_KEY": Core.generate_secret(64),
            "JWT_PAYLOAD_ENCRYPTION_KEY": Core.generate_fernet(),
        }

        with open(ENV_FILE) as f:
            content = f.read()

        for key, value in replaces.items():
            content = content.replace(f'<{key}>', value)

        with open(ENV_FILE, "w") as f:
            f.write(content)

        print(S.info(f"Secrets writen to environment file: {ENV_FILE}"), S.success("[OK]"))
        print(S.warning("!KEEP THEM SAFE!"))


class ProxyMixin(object):
    def get_command(self, cmd: str, args: str):
        return {
            "default": ["method", ("arg1", "arg2"), ],
        }

    def _get_command(self, cmd: str, args: str):
        return self.get_command(cmd, args).get(cmd)

    def cmd(self, tpl: str, cmd: str, args: str):
        return [self.format(tpl, cmd, args), ]

    def format(self, tpl: str, cmd: str, args: str):
        return tpl.format(**{
            "ENV": ENV,
            "PROJECT_NAME": PROJECT_NAME,
            "APP_NAME": APP_NAME,
            "APP_PORT": APP_PORT,
            "COMPOSE": COMPOSE,
            "ENV_FILE": ENV_FILE,
            "cmd": cmd,
            "args": args,
        })

    def command(self, c, cmd, args: str):
        _cmd = self._get_command(cmd, args)
        if cmd is None:
            print(S.danger(f"ERROR: command not found: '{cmd}'"))
            return
        method, method_args = _cmd
        cmds = method(*method_args)
        for n, _c in enumerate(cmds):
            print(S.info(f"[{n+1}/{len(cmds)}]"), S.secondary(_c))
            if not TEST_MODE:
                c.run(_c)


class DockerTasks(ProxyMixin):
    def get_command(self, cmd: str, args: str):
        tpl = "docker compose -f {COMPOSE} {cmd} {args}"
        default_args = (tpl, cmd, args)
        return {
            "ps": (self.cmd, default_args),
            "build": (self.cmd, default_args),
            "up": (self.cmd, (tpl, cmd, "-d")),
            "down": (self.cmd, default_args),
            "start": (self.cmd, default_args),
            "stop": (self.cmd, default_args),
            "restart": (self.cmd, default_args),
            "logs": (self.cmd, (
                "docker compose -f {COMPOSE} logs {APP_NAME} {args}",
                cmd,
                args or "--tail 100 -f"
            )),
            "bash": (
                self.cmd, (
                    "docker compose -f {COMPOSE} exec {APP_NAME} bash {args}", cmd, args
                )),
            "rebuild": (self.rebuild, default_args),
        }

    def rebuild(self, tpl: str, cmd: str, args: str):
        return [
            self.format(tpl, "down", args),
            self.format(tpl, "build --no-cache", args),
            self.format(tpl, "up -d", args),
        ]


class DjangoTasks(ProxyMixin):
    def get_command(self, cmd: str, args: str):
        tpl = "docker compose -f {COMPOSE} exec {APP_NAME} python manage.py {cmd} {args}"
        default_args = (tpl, cmd, args)
        return {
            "shell": (self.cmd, (tpl, "shell_plus", args)),
            "makemigrations": (self.cmd, default_args),
            "migrate": (self.cmd, default_args),
            "showmigrations": (self.cmd, default_args),
            "collectstatic": (self.cmd, default_args),
            "createsuperuser": (self.cmd, default_args),
            "startapp": (self.startapp, default_args),
        }

    def startapp(self, tpl: str, cmd: str, args: str):
        # args - must start with app_name
        app_name, *args = args.strip().split(" ")
        if not app_name:
            print(S.danger(f"ERROR: `app_name` wan not provided"))
            return []
        return [
            f"mkdir -p apps/{app_name}",
            self.format(tpl, f"startapp {app_name}", f"apps/{app_name}"),
        ]


# TASKS DEFINITION
INSTALL = InstallTasks()
DOCKER = DockerTasks()
DJANGO = DjangoTasks()

@task
def setup(c):
    INSTALL.setup(c)

@task
def keygen(c):
    INSTALL.keygen(c)

@task
def docker(c, cmd, args=""):
    DOCKER.command(c, cmd, args)

@task
def django(c, cmd, args=""):
    DJANGO.command(c, cmd, args)

@task
def dj(c, cmd, args=""):
    # alias for `django`
    DJANGO.command(c, cmd, args)
