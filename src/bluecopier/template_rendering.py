import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Any, NamedTuple, cast

import jinja2
from jinja2.utils import missing

import bluecopier

if TYPE_CHECKING:
    from bluecopier.blueprint.blueprint import Blueprint

ROOT_DIR = Path(bluecopier.__file__).parent.parent.parent
BLUEPRINT_DIR = ROOT_DIR / "blueprints"


class EnvironmentOverrides(NamedTuple):
    line_statement_prefix: str | missing = missing
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
                line_statement_prefix=overrides.line_statement_prefix,
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
        user_options = blueprint.project.user_options
        context = {
            "blueprint": blueprint,
            "project_name": user_options.project_name,
            "python_version": user_options.python_version,
            "author_name": user_options.author_name,
            "author_email": user_options.author_email,
            "license": user_options.license_,
        }
        rendered = template.render(source_path=source_path, context=context)
    return rendered
