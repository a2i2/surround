.. _surround-api:

API
*****************
Here you can find documentation on all classes and their methods in Surround.

Surround
========

.. automodule:: surround

    .. autoclass:: Surround
        :members:

        .. automethod:: __init__   

    .. automodule:: surround.config

    Config     
    ^^^^^^
    
    .. autoclass:: surround.config.Config       
        :members:   
    
        .. automethod:: __init__  

        .. automethod:: __getitem__  

        .. automethod:: __iter__          

        .. automodule:: surround

    SurroundData  
    ^^^^^^^^^^^^
    
    .. autoclass:: surround.SurroundData        
        :members:          

    .. automodule:: surround.stage

    Stage
    ^^^^^
    
    .. autoclass:: surround.stage.Stage
        :members:         

Wrapper
=======
.. autoclass:: surround.Wrapper  
    :members:

    .. automethod:: __init__

AllowedTypes    
^^^^^^^^^^^^

.. autoclass:: surround.AllowedTypes 
    :show-inheritance:
    :members:

Linter
======

.. automodule:: surround.linter 
    
    .. autoclass:: Linter
        :members:

    LinterStage
    ^^^^^^^^^^^
    
    .. autoclass:: LinterStage
        :show-inheritance:
        :members:

        .. automethod:: __init__

    ProjectData
    ^^^^^^^^^^^

    .. autoclass:: ProjectData
        :show-inheritance:
        :members:

    CheckData
    ^^^^^^^^^

    .. autoclass:: CheckData
        :show-inheritance: 
        :members:

    CheckFiles
    ^^^^^^^^^^

    .. autoclass:: CheckFiles
        :show-inheritance:
        :members:

    CheckDirectories
    ^^^^^^^^^^^^^^^^

    .. autoclass:: CheckDirectories
        :show-inheritance:
        :members:                       

Web API
=======

.. automodule:: surround.runner.web.api

    .. autofunction:: make_app

    HealthCheck
    ^^^^^^^^^^^
    .. autoclass:: HealthCheck
        :members:
        :show-inheritance:

    Upload
    ^^^^^^
    .. autoclass:: Upload
        :members:
        :show-inheritance:

    Predict
    ^^^^^^^
    .. autoclass:: Predict
        :members:    
        :show-inheritance: