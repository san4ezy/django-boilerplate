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


class InstallTasks:
    def setup(self, c):
        # If you cannot install fabric and dotenv globally it will not work
        env_dir = Path("environments") / ENV

        print(S.info("Env directory"), S.normal(env_dir))
        # os.makedirs(env_dir, exist_ok=True)
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


class DockerTasks:
    _command = f"docker-compose -f {COMPOSE}"

    def command(self, c, cmd):
        cmd = f"{self._command} {cmd}"
        print(S.secondary(cmd))
        c.run(cmd, pty=True)


class DjangoTasks:
    _command = f"docker-compose -f {COMPOSE} exec {APP_NAME} python manage.py"

    def command(self, c, cmd, extra_args=""):
        cmd = f"{self._command} {cmd} {extra_args}"
        print(S.secondary(cmd))
        c.run(cmd, pty=True)

    def startapp(self, c, app_name: str):
        c.run(f"mkdir apps/{app_name}", pty=True)
        self.command(c, f"startapp {app_name} apps/{app_name}")

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
def build(c):
    DOCKER.command(c, "build")

@task
def rebuild(c, nocache=False):
    DOCKER.command(c, "down")
    DOCKER.command(c, f"build {'--nocache' if nocache else ''}")
    DOCKER.command(c, "up -d")

@task
def up(c):
    DOCKER.command(c, "up -d")

@task
def down(c):
    DOCKER.command(c, "down")

@task
def ps(c):
    DOCKER.command(c, "ps")

@task
def logs(c):
    DOCKER.command(c, f"logs {APP_NAME} --tail 100 -f")

@task
def start(c):
    DOCKER.command(c, "start")

@task
def stop(c):
    DOCKER.command(c, "stop")

@task
def restart(c):
    DOCKER.command(c, "restart")

@task
def bash(c):
    DOCKER.command(c, f"exec {APP_NAME} bash")

@task
def shell(c):
    DJANGO.command(c, "shell_plus")

@task
def migrations(c, cmd, extra_args=""):
    cmd = dict(
        show="showmigrations",
        make="makemigrations",
        migrate="migrate",
    )[cmd]
    DJANGO.command(c, cmd, extra_args)

@task
def collectstatic(c):
    DJANGO.command(c, "collectstatic -y")

@task
def createsuperuser(c):
    DJANGO.command(c, "createsuperuser")

@task
def startapp(c, app_name: str):
    DJANGO.startapp(c, app_name)
