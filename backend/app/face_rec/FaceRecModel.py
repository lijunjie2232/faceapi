class FaceRecModel:
    """
    A registry to manage model classes and provide instances of registered models.
    """

    _models = {}

    @classmethod
    def register(cls, name):
        """
        Decorator to register a model class with a given name.

        Args:
            name (str): Name to register the model under

        Returns:
            function: Decorator function
        """

        def decorator(model_class):
            cls._models[name] = model_class
            model_class.name = name
            return model_class

        return decorator

    @classmethod
    def get_model(cls, name, *args, **kwargs):
        """
        Get an instance of a registered model.

        Args:
            name (str): Name of the model to instantiate
            *args: Arguments to pass to the model constructor
            **kwargs: Keyword arguments to pass to the model constructor

        Returns:
            object: Instance of the requested model

        Raises:
            ValueError: If the model name is not registered
        """
        if name not in cls._models:
            raise ValueError(f"Model '{name}' is not registered.")

        model_class = cls._models[name]
        return model_class(*args, **kwargs)

    @classmethod
    def list_models(cls):
        """
        List all registered model names.

        Returns:
            list: List of registered model names
        """
        return list(cls._models.keys())

    @classmethod
    def has_model(cls, name):
        """
        Check if a model is registered.

        Args:
            name (str): Name of the model to check

        Returns:
            bool: True if the model is registered, False otherwise
        """
        return name in cls._models


# Create convenient functions for external usage
register_model = FaceRecModel.register
get_model = FaceRecModel.get_model
list_models = FaceRecModel.list_models
has_model = FaceRecModel.has_model
