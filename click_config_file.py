import os
import click
import configobj


class configobj_provider:
    def __init__(self, unrepr=True, section=None):
        self.unrepr = unrepr
        self.section = section

    def __call__(self, file_path, cmd_name):
        config = configobj.ConfigObj(file_path, unrepr=self.unrepr)
        if self.section:
            config = config[self.section].dict()
        return config


def configuration_option(*param_decls, **attrs):
    def decorator(f):
        def callback(ctx, param, value):
            nonlocal cmd_name, config_file_name, saved_callback, provider
            if not ctx.default_map:
                ctx.default_map = {}
            if not cmd_name:
                cmd_name = ctx.info_name
            default_value = os.path.join(
                click.get_app_dir(cmd_name), config_file_name)
            param.default = default_value
            if not value:
                value = default_value
            try:
                config = provider(value, cmd_name)
            except Exception as e:
                raise click.BadOptionUsage(
                    "Error reading configuration file: {}".format(e), ctx)
            ctx.default_map.update(config)
            return saved_callback(ctx, param, value) if saved_callback else value

        attrs.setdefault('is_eager', True)
        attrs.setdefault('help', 'Read configuration from PATH.')
        attrs.setdefault('expose_value', False)
        cmd_name = attrs.pop('cmd_name', None)
        config_file_name = attrs.pop('config_file_name', 'config')
        provider = attrs.pop('provider', configobj_provider())
        path_default_params = {
            'exists': False,
            'file_okay': True,
            'dir_okay': False,
            'writable': False,
            'readable': True,
            'resolve_path': False
        }
        path_params = {k: attrs.pop(k, v) for k, v in path_default_params.items()}
        attrs['type'] = click.Path(**path_params)
        saved_callback = attrs.pop('callback', None)
        attrs['callback'] = callback
        return click.option(*(param_decls or ('--config', )), **attrs)(f)

    return decorator
