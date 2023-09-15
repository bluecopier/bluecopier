import inspect
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, NamedTuple, cast

import jinja2
from jinja2 import TemplateError

import bluecopier

if TYPE_CHECKING:
    from bluecopier.blueprint.blueprint import Blueprint

ROOT_DIR = Path(bluecopier.__file__).parent.parent.parent
BLUEPRINT_DIR = ROOT_DIR / "blueprints"
logger = logging.getLogger("tpl")


class EnvironmentOverrides(NamedTuple):
    line_statement_prefix: str | None = None
    block_start_string: str = "{%"
    block_end_string: str = "%}"
    variable_start_string: str = "{{"
    variable_end_string: str = "}}"
    comment_start_string: str = "{#"
    comment_end_string: str = "#}"


_default_override = EnvironmentOverrides()

# The goal with this is to provide a syntax that allows the template itself to be
# developed on, so for instance if you're using a template for a Python project,
# you can use Python syntax in the template itself, e.g:
#
# # ! if feature.type_checking
# # ! endif
LANGUAGE_OVERRIDES: dict[str, EnvironmentOverrides] = {
    "py": EnvironmentOverrides(line_statement_prefix="# !"),
    "tf": EnvironmentOverrides(line_statement_prefix="// !"),
    # Note: github yaml uses ${{
    "yml": EnvironmentOverrides(
        variable_start_string="<<",
        variable_end_string=">>",
    ),
    "toml": EnvironmentOverrides(variable_start_string="${", variable_end_string="}"),
}


def current_frame_lineno() -> int | None:
    frame = inspect.currentframe()
    assert frame is not None
    assert frame.f_back is not None
    jinja_template = frame.f_globals.get("__jinja_template__")
    assert jinja_template is not None
    lineno = jinja_template.get_corresponding_lineno(frame.f_back.f_lineno)
    return cast(int | None, lineno)


def jinja2_template_error_lineno() -> int | None:
    exc_type, value, tb = sys.exc_info()
    if exc_type is None or not issubclass(exc_type, TemplateError):
        return None
    if value is not None and hasattr(value, "lineno"):
        # in case of TemplateSyntaxError
        return cast(int, value.lineno)
    while tb:
        if tb.tb_frame.f_code.co_filename == "<template>":
            return tb.tb_lineno
        tb = tb.tb_next
    return None


class Template(jinja2.Template):
    def render(self, source_path: Path, context: dict[str, Any]) -> str:
        context["__filename__"] = str(source_path)
        context["__lineno__"] = current_frame_lineno
        return super().render(context)


class Environment(jinja2.Environment):
    template_class = Template

    def contains_jinja_statements(self, content: str) -> bool:
        if self.line_statement_prefix:
            for line in content.splitlines():
                if line.startswith(self.line_statement_prefix):
                    return True
        if self.block_start_string in content:
            return True
        if self.variable_start_string in content:
            return True
        return False


# This is needed because jinja2 doesn't support setting line_statement_prefix per template,
# and we want to use different comment characters for different source files.
_environments: dict[str, Environment] = {}

# This is shared between all environments, so that we can use the same filters in all templates.
_shared_environment = Environment()


def get_environment_for_path(path: Path) -> Environment:
    ext = path.suffix[1:]
    environment = _environments.get(ext)
    if environment is None:
        overrides = LANGUAGE_OVERRIDES.get(ext, _default_override)
        environment = cast(
            Environment,
            _shared_environment.overlay(
                block_end_string=overrides.block_end_string,
                block_start_string=overrides.block_start_string,
                comment_start_string=overrides.comment_start_string,
                comment_end_string=overrides.comment_end_string,
                # bug in types-jinja2, should allow str | None
                line_statement_prefix=cast(str, overrides.line_statement_prefix),
                variable_start_string=overrides.variable_start_string,
                variable_end_string=overrides.variable_end_string,
            ),
        )
        _environments[ext] = environment
    return environment


def maybe_render_jinja_template(*, source_path: Path, content: str, blueprint: "Blueprint") -> str | None:
    environment = get_environment_for_path(source_path)
    rendered = None
    if environment.contains_jinja_statements(content):
        try:
            template = environment.from_string(content)
        except jinja2.TemplateSyntaxError as exc:
            raise jinja2.TemplateSyntaxError(
                f"Error in {source_path}: {exc.message}",
                exc.lineno,
                exc.name,
                exc.filename,
            ) from exc
        project = blueprint.project
        project_context = project.get_template_context()

        context = {
            "blueprint": blueprint,
            **project_context,
        }

        try:
            rendered = template.render(source_path=source_path, context=context)
        except jinja2.UndefinedError as exc:
            path = source_path.relative_to(blueprint.root_path)
            lineno_number = jinja2_template_error_lineno()
            lineno = ":" + str(lineno_number) if lineno_number else ""
            logger.exception(f"blueprint/{blueprint.name}/{path}{lineno}: {exc.message}")
            raise SystemExit from exc

    return rendered
