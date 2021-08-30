.. _surround-api:

API Reference
*****************
Here you can find documentation on all classes and their methods in Surround.

.. _assembler:   

Assembler
========

.. autodata:: surround.assembler.Assembler
    :no-value:

    .. automethod:: surround.assembler.Assembler.init_assembler
    .. automethod:: surround.assembler.Assembler.run
    .. automethod:: surround.assembler.Assembler.set_config
    .. automethod:: surround.assembler.Assembler.set_stages
    .. automethod:: surround.assembler.Assembler.set_finaliser
    .. automethod:: surround.assembler.Assembler.set_metrics


.. automodule:: surround

BaseConfig
==========
    
.. autodata:: surround.config.BaseConfig       
    :no-value:

SurroundConfig
==============

.. autodata:: surround.config.SurroundConfig       
    :no-value:

@config
=======

.. autodecorator:: surround.config.config

load_config
===========

.. autofunction:: surround.config.load_config
 
State                              
=====
                
.. autoclass:: surround.State        
    :members:                   

.. automodule:: surround.stage

Stage
=====
    
.. autoclass:: surround.stage.Stage
    :members:

Estimator
=========

.. autoclass:: surround.stage.Estimator
    :members:

Runner
=======
.. autoclass:: surround.runners.Runner  
    :members:

