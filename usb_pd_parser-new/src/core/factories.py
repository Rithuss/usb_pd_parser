"""Factory helpers for parsers, writers and validators.

Provides simple registries to register and instantiate components
by string key. Factories return new instances of registered
classes and expose helper methods to inspect available types.
"""
from typing import Dict, Optional, Type
from pathlib import Path


class ParserFactory:
    """Registry and factory for parser classes.

    Register parser classes with ``register_parser`` and create
    instances with ``create_parser`` by passing the registered
    type name and a `doc_title`.
    """
    
    # ENCAPSULATION: Private registry of parser types
    __parser_registry: Dict[str, Type] = {}
    
    @staticmethod
    def register_parser(parser_type: str, parser_class: Type):
        """Register a parser class under a short string key."""
        ParserFactory.__parser_registry[parser_type] = parser_class
    
    @staticmethod
    def create_parser(parser_type: str, doc_title: str, **kwargs):
        """Instantiate a regis                                                                  tered parser class.

        Raises ValueError when the type is unknown.
        """
        parser_class = ParserFactory.__parser_registry.get(parser_type)
        
        if parser_class is None:
            available = ', '.join(ParserFactory.__parser_registry.keys())
            raise ValueError(
                f"Unknown parser type: '{parser_type}'. "
                f"Available types: {available}"
            )
        
        # Create and return parser instance
        return parser_class(doc_title, **kwargs)
    
    @staticmethod
    def get_registered_parsers() -> list:
        """Return a list of registered parser type names."""
        return list(ParserFactory.__parser_registry.keys())
    
    @staticmethod
    def is_registered(parser_type: str) -> bool:
        """Return True when `parser_type` has been registered."""
        return parser_type in ParserFactory.__parser_registry
    
    def __str__(self) -> str:
        """Return a short description listing registered parser keys."""
        types = ', '.join(ParserFactory.__parser_registry.keys())
        return f"ParserFactory(types=[{types}])"


class WriterFactory:
    """Registry and factory for writer classes.

    Register writers with ``register_writer`` and create instances
    with ``create_writer`` by providing a type key and output path.
    """
    
    # ENCAPSULATION: Private registry
    __writer_registry: Dict[str, Type] = {}
    
    @staticmethod
    def register_writer(writer_type: str, writer_class: Type):
        """Register a writer class under a short string key."""
        WriterFactory.__writer_registry[writer_type] = writer_class
    
    @staticmethod
    def create_writer(
        writer_type: str,
        output_path: str,
        **kwargs
    ):
        """Instantiate a registered writer class for the given path."""
        writer_class = WriterFactory.__writer_registry.get(writer_type)
        
        if writer_class is None:
            available = ', '.join(WriterFactory.__writer_registry.keys())
            raise ValueError(
                f"Unknown writer type: '{writer_type}'. "
                f"Available types: {available}"
            )
        
        return writer_class(output_path, **kwargs)
    
    @staticmethod
    def get_registered_writers() -> list:
        """Return a list of registered writer type names."""
        return list(WriterFactory.__writer_registry.keys())
    
    @staticmethod
    def is_registered(writer_type: str) -> bool:
        """Return True when `writer_type` has been registered."""
        return writer_type in WriterFactory.__writer_registry
    
    def __str__(self) -> str:
        """Return a short description listing registered writer keys."""
        types = ', '.join(WriterFactory.__writer_registry.keys())
        return f"WriterFactory(types=[{types}])"


class ValidatorFactory:
    """Registry and factory for validator strategy classes."""
    
    # ENCAPSULATION: Private registry
    __validator_registry: Dict[str, Type] = {}
    
    @staticmethod
    def register_validator(
        validator_type: str,
        validator_class: Type
    ):
        """Register a validator class under a short string key."""
        ValidatorFactory.__validator_registry[validator_type] = (
            validator_class
        )
    
    @staticmethod
    def create_validator(validator_type: str, **kwargs):
        """Instantiate a registered validator class.

        Raises ValueError when the type is unknown.
        """
        validator_class = ValidatorFactory.__validator_registry.get(
            validator_type
        )
        
        if validator_class is None:
            available = ', '.join(
                ValidatorFactory.__validator_registry.keys()
            )
            raise ValueError(
                f"Unknown validator type: '{validator_type}'. "
                f"Available types: {available}"
            )
        
        return validator_class(**kwargs)
    
    @staticmethod
    def get_registered_validators() -> list:
        """Return a list of registered validator type names."""
        return list(ValidatorFactory.__validator_registry.keys())
    
    @staticmethod
    def is_registered(validator_type: str) -> bool:
        """Return True when `validator_type` has been registered."""
        return validator_type in ValidatorFactory.__validator_registry
    
    def __str__(self) -> str:
        """Return a short description listing registered validator keys."""
        types = ', '.join(
            ValidatorFactory.__validator_registry.keys()
        )
        return f"ValidatorFactory(types=[{types}])"


# Convenience function for factory pattern
def create_component(
    component_type: str,
    factory_type: str,
    **kwargs
):
    """Convenience wrapper to create a component from the named factory.

    `component_type` must be one of: 'parser', 'writer', 'validator'.
    The function dispatches to the appropriate factory create method.
    """
    factories = {
        'parser': ParserFactory,
        'writer': WriterFactory,
        'validator': ValidatorFactory
    }

    factory = factories.get(component_type)
    if factory is None:
        raise ValueError(
            f"Unknown component type: {component_type}"
        )

    return factory.create_parser(factory_type, **kwargs)


# Module exports
__all__ = [
    'ParserFactory',
    'WriterFactory',
    'ValidatorFactory',
    'create_component'
]