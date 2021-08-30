import unittest
from dataclasses import dataclass
from typing import Optional
from surround import Assembler, Estimator, State, BaseConfig, config as surround_config, load_config, Stage

test_text = "hello"

@dataclass
class HelloStageData:
    suffix: Optional[str] = None

@surround_config(name="config")
@dataclass
class Config(BaseConfig):
    helloStage: Optional[HelloStageData] = None

class HelloStage(Estimator):
    def estimate(self, state, config):
        if state.estimator_add_error:
            state.errors.append("Error!!")
        elif state.estimator_throw:
            raise Exception("Error!!")

        state.text = test_text
        if not isinstance(config, BaseConfig) and config.helloStage:
            state.config_value = config["helloStage"]["suffix"]

    def fit(self, state, config):
        print("No training implemented")


# pylint: disable=too-many-instance-attributes
class AssemblerState(State):
    def __init__(self):
        super().__init__()
        self.errors = []
        self.text = None
        self.config_value = None
        self.stage1 = None
        self.final_ran = False
        self.use_errors_instead = False
        self.post_filter_ran = False
        self.post_filter_throw = False
        self.validator_add_error = False
        self.estimator_throw = False
        self.estimator_add_error = False

class InputValidator(Stage):
    def operate(self, state, config):
        if state.text:
            raise ValueError("'text' is not None")

        if state.config_value:
            raise ValueError("'config_value' is not None")

        if state.stage1:
            raise ValueError("'stage1' is not None")

        if state.validator_add_error:
            state.errors.append("Error!!")

class BadFilter(Stage):
    def initialise(self, config):
        raise Exception("This will fail always")

    def operate(self, state, config):
        if state.use_errors_instead:
            state.errors.append("This will fail always")
        else:
            raise Exception("This will fail always")

class PostFilter(Stage):
    def operate(self, state, config):
        state.post_filter_ran = True

class TestFinalStage(Stage):
    def operate(self, state, config):
        state.final_ran = True

class TestSurround(unittest.TestCase):

    def test_happy_path(self):
        data = AssemblerState()
        assembler = Assembler("Happy path").set_stages([InputValidator(), HelloStage()]).set_config(Config())
        assembler.init_assembler()
        assembler.run(data)
        self.assertEqual(data.text, test_text)

    def test_rejecting_attributes(self):
        data = AssemblerState()
        assembler = Assembler("Reject attribute").set_stages([InputValidator(), HelloStage()]).set_config(Config())
        assembler.init_assembler()
        assembler.run(data)
        self.assertRaises(AttributeError, getattr, data, "no_text")

    def test_surround_config(self):
        config = load_config(name="config", config_class=Config)
        data = AssemblerState()
        assembler = Assembler("Surround config").set_stages([InputValidator(), HelloStage()]).set_config(config)
        assembler.run(data)
        self.assertEqual(data.config_value, "Scott")

    def test_finaliser_successful_pipeline(self):
        data = AssemblerState()
        assembler = Assembler("Finalizer test").set_stages([InputValidator(), HelloStage()]).set_config(Config())
        assembler.set_finaliser(TestFinalStage())
        assembler.init_assembler()

        # Run assembler which will succeed
        assembler.run(data)

        # Finalizer should be executed
        self.assertTrue(data.final_ran)

    def test_finaliser_fail_pipeline(self):
        # Ensure pipeline will crash
        data = AssemblerState()
        data.text = ""

        assembler = Assembler("Finalizer test").set_stages([InputValidator(), HelloStage()]).set_config(Config())
        assembler.set_finaliser(TestFinalStage())
        assembler.init_assembler()

        # Run assembler which will fail
        assembler.run(data)

        # Finalizer should still be executed
        self.assertTrue(data.final_ran)

    def test_assembler_init_pass(self):
        assembler = Assembler("Pass test").set_stages([InputValidator(), HelloStage()])
        self.assertTrue(assembler.init_assembler())

    def test_assembler_init_fail(self):
        assembler = Assembler("Fail test").set_stages([InputValidator(), BadFilter(), HelloStage()])
        self.assertFalse(assembler.init_assembler())

    def test_pipeline_stop_on_exception_estimator(self):
        data = AssemblerState()
        data.estimator_throw = True

        assembler = Assembler("Fail test").set_stages([InputValidator(), HelloStage(), PostFilter()])

        # This should fail to execute PostFilter
        assembler.run(data)

        self.assertFalse(data.post_filter_ran)

    def test_pipeline_stop_on_error_estimator(self):
        data = AssemblerState()
        data.estimator_add_error = True

        assembler = Assembler("Fail test").set_stages([InputValidator(), HelloStage(), PostFilter()])

        # This should fail to execute PostFilter
        assembler.run(data)

        self.assertFalse(data.post_filter_ran)

    def test_pipeline_stop_on_exception_filter(self):
        data = AssemblerState()

        assembler = Assembler("Fail test").set_stages([InputValidator(), BadFilter(), HelloStage(), PostFilter()])

        # This should fail to execute HelloStage
        assembler.run(data)

        self.assertIsNone(data.text)
        self.assertFalse(data.post_filter_ran)

    def test_pipeline_stop_on_error_filter(self):
        # Use the errors list in state instead
        data = AssemblerState()
        data.use_errors_instead = True

        assembler = Assembler("Fail test").set_stages([InputValidator(), BadFilter(), HelloStage(), PostFilter()])

        # This should fail to execute HelloStage & PostFilter
        assembler.run(data)

        self.assertIsNone(data.text)
        self.assertFalse(data.post_filter_ran)

    def test_pipeline_stop_on_exception_validator(self):
        data = AssemblerState()
        data.stage1 = "Now it will fail in the validator"

        assembler = Assembler("Fail test").set_stages([InputValidator(), HelloStage(), PostFilter()])

        # This should fail to execute HelloStage & PostFilter
        assembler.run(data)

        self.assertIsNone(data.text)
        self.assertFalse(data.post_filter_ran)

    def test_pipeline_stop_on_error_validator(self):
        data = AssemblerState()
        data.validator_add_error = True

        assembler = Assembler("Fail test").set_stages([InputValidator(), HelloStage(), PostFilter()])

        # This should fail to execute HelloStage & PostFilter
        assembler.run(data)

        self.assertIsNone(data.text)
        self.assertFalse(data.post_filter_ran)
