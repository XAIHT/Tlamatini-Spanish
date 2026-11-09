# Tlamatini Author Banner — Created by Angela López Mendoza · @angelahack1
"""The real Django account wizard, without unrelated web/LLM startup checks."""

import os
import sys

from django.contrib.auth.management.commands.createsuperuser import Command as CreateSuperuser
from django.core.checks import Tags


class Command(CreateSuperuser):
    # Keep model consistency, migration checks, duplicate-name validation and
    # Django's password validation. URL checks import the entire chat application
    # but have no bearing on an interactive auth-user creation.
    requires_system_checks = [Tags.models]

    def run_from_argv(self, argv):
        try:
            return super().run_from_argv(argv)
        finally:
            # Retain only a console launched by the integrated wizard. Manual
            # command use and --noinput automation retain normal Django behavior.
            if (os.environ.get('TLAMATINI_USER_WIZARD') == '1'
                    and '--noinput' not in argv and '--no-input' not in argv
                    and sys.stdin.isatty()):
                try:
                    input('\nPulsa Intro para cerrar esta consola. ')
                except (EOFError, KeyboardInterrupt):
                    pass
