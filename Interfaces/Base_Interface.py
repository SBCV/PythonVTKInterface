
class BaseInterface(object):

    def init_instance_variable(self, instance_var_str, value, default_value):
        if value is not None:
            setattr(self, instance_var_str, value)
        else:
            setattr(self, instance_var_str, default_value)
