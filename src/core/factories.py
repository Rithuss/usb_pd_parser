"""
Factories Module
Implements Factory Pattern for creating objects.

OOP Concepts:
- Factory Pattern
- @staticmethod decorator
- Dependency Injection
- Type-safe object creation
"""
from typing import Dict, Optional, Type
from pathlib import Path


class ParserFactory:
    """
    Factory for creating parser instances (Factory Pattern).
    
    OOP Principles:
    - FACTORY PATTERN: Creates objects without specifying exact class
    - ENCAPSULATION: Hides object creation complexity
    """
    
    # ENCAPSULATION: Private registry of parser types
    __parser_registry: Dict[str, Type] = {}
    
    @staticmethod
    def register_parser(parser_type: str, parser_class: Type):
        """
        Register a parser class (DEPENDENCY INJECTION).
        
        Args:
            parser_type: Type identifier (e.g., 'toc', 'spec')
            parser_class: Parser class to register
        """
        ParserFactory.__parser_registry[parser_type] = parser_class
    
    @staticmethod
    def create_parser(parser_type: str, doc_title: str, **kwargs):
        """
        Create parser instance (FACTORY PATTERN).
        
        Args:
            parser_type: Type of parser to create
            doc_title: Document title
            **kwargs: Additional arguments for parser
            
        Returns:
            Parser instance
            
        Raises:
            ValueError: If parser type not registered
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
        """
        Get list of registered parser types.
        
        Returns:
            List of parser type names
        """
        return list(ParserFactory.__parser_registry.keys())
    
    @staticmethod
    def is_registered(parser_type: str) -> bool:
        """
        Check if parser type is registered.
        
        Args:
            parser_type: Parser type to check
            
        Returns:
            True if registered
        """
        return parser_type in ParserFactory.__parser_registry
    
    # SPECIAL METHOD: String representation
    def __str__(self) -> str:
        """Human-readable representation"""
        types = ', '.join(ParserFactory.__parser_registry.keys())
        return f"ParserFactory(types=[{types}])"


class WriterFactory:
    """
    Factory for creating writer instances (Factory Pattern).
    
    OOP: Encapsulates writer object creation
    """
    
    # ENCAPSULATION: Private registry
    __writer_registry: Dict[str, Type] = {}
    
    @staticmethod
    def register_writer(writer_type: str, writer_class: Type):
        """
        Register a writer class.
        
        Args:
            writer_type: Type identifier (e.g., 'jsonl', 'json')
            writer_class: Writer class to register
        """
        WriterFactory.__writer_registry[writer_type] = writer_class
    
    @staticmethod
    def create_writer(
        writer_type: str,
        output_path: str,
        **kwargs
    ):
        """
        Create writer instance (FACTORY PATTERN).
        
        Args:
            writer_type: Type of writer to create
            output_path: Output file path
            **kwargs: Additional arguments
            
        Returns:
            Writer instance
            
        Raises:
            ValueError: If writer type not registered
        """
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
        """Get list of registered writer types"""
        return list(WriterFactory.__writer_registry.keys())
    
    @staticmethod
    def is_registered(writer_type: str) -> bool:
        """Check if writer type is registered"""
        return writer_type in WriterFactory.__writer_registry
    
    # SPECIAL METHOD
    def __str__(self) -> str:
        """String representation"""
        types = ', '.join(WriterFactory.__writer_registry.keys())
        return f"WriterFactory(types=[{types}])"


class ValidatorFactory:
    """
    Factory for creating validator instances (Strategy Pattern).
    
    OOP: Creates validation strategies dynamically
    """
    
    # ENCAPSULATION: Private registry
    __validator_registry: Dict[str, Type] = {}
    
    @staticmethod
    def register_validator(
        validator_type: str,
        validator_class: Type
    ):
        """
        Register a validator class.
        
        Args:
            validator_type: Type identifier
            validator_class: Validator class to register
        """
        ValidatorFactory.__validator_registry[validator_type] = (
            validator_class
        )
    
    @staticmethod
    def create_validator(validator_type: str, **kwargs):
        """
        Create validator instance (FACTORY PATTERN).
        
        Args:
            validator_type: Type of validator to create
            **kwargs: Additional arguments
            
        Returns:
            Validator instance
            
        Raises:
            ValueError: If validator type not registered
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
        """Get list of registered validator types"""
        return list(ValidatorFactory.__validator_registry.keys())
    
    @staticmethod
    def is_registered(validator_type: str) -> bool:
        """Check if validator type is registered"""
        return validator_type in ValidatorFactory.__validator_registry
    
    # SPECIAL METHOD
    def __str__(self) -> str:
        """String representation"""
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
    """
    Universal component creator (FACTORY PATTERN).
    
    Args:
        component_type: Type of component (parser/writer/validator)
        factory_type: Specific type to create
        **kwargs: Arguments for component
        
    Returns:
        Component instance
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