from abc import abstractmethod, ABCMeta
from ..dispatching import call_method_or_dispatch, create_registerer
from toolz.dicttoolz import merge_with
from itertools import starmap, repeat
from operator import __add__, __mul__, __sub__, methodcaller
from frozendict import frozendict
from six import PY3, PY2
from types import MethodType
from toolz.functoolz import curry, flip as tzflip
from toolz.curried import valmap
from sympy.core.symbol import Symbol
from sklearn.base import BaseEstimator
import re

def safe_symbol(s):
    if isinstance(s, Symbol):
        return s
    return Symbol(s)

class VariableFactory(object):
    def __init__(self, base='x', existing=[]):
        self.base = base
        self.existing = set(map(safe_symbol, existing))
        self.current_n = self._get_current_n()
        
    
    def _get_current_n(self):
        regex = re.compile('%s(\d+)' % self.base)
        result = -1
        for sym in self.existing:
            match = regex.match(sym.name)
            if match:
                val = int(match.group(1))
                if val > result:
                    result = val
        result += 1
        return result
    
    def __call__(self):
        result = self.base + str(self.current_n)
        self.current_n += 1
        return result

class NamingSchemeBase(object):
    __metaclass__ = ABCMeta
    def name(self, function):
        '''
        Assign names to Function and any Functions called by Function.
        
        Parameters
        ----------
        function : instance of Function
        
        Returns
        -------
        dict with keys Functions and values strs
        '''

class SerializerBase(object):
    __metaclass__ = ABCMeta
    def serialize(self, functions):
        '''
        Serialize the function.
        
        Parameters
        ----------
        functions : dict with keys strs and values instances of Function.  The keys are typically used to 
        name the functions.
        
        Returns
        -------
        str
            A string representing the serialized Functions.  Usually this should be written to a file.
        '''
        return self._serialize(functions)
    
    @abstractmethod
    def _serialize(self, function):
        pass
    
class PrinterTemplateSerializer(SerializerBase):
    def __init__(self, printer, template):
        '''
        Parameters
        ----------
        printer : An instance of a CodePrinter subclass from sympy.
        template : A mako template.
        
        '''
        self.printer = printer
        self.template = template



sym_decision_function_doc = '''
Parameters
----------
estimator : A scikit-learn or other compatible fitted classifier.

Returns
-------
Function
    A Function object specifying the decision function for estimator.

Raises
------
NotFittedError
    When the estimator is not fitted.

NotImplementedError
    When the estimator's type is not supported.

'''
sym_decision_function_dispatcher = {}
sym_decision_function = call_method_or_dispatch('sym_decision_function', sym_decision_function_dispatcher, docstring=sym_decision_function_doc)
register_sym_decision_function = create_registerer(sym_decision_function_dispatcher, 'register_sym_decision_function')

sym_predict_proba_doc = '''
Parameters
----------
estimator : A scikit-learn or other compatible fitted classifier.

Returns
-------
Function
    A Function object specifying the predict_proba function for estimator.

Raises
------
NotFittedError
    When the estimator is not fitted.

NotImplementedError
    When the estimator's type is not supported.

'''
sym_predict_proba_dispatcher = {}
sym_predict_proba = call_method_or_dispatch('sym_predict_proba', sym_predict_proba_dispatcher, docstring=sym_predict_proba_doc)
register_sym_predict_proba = create_registerer(sym_predict_proba_dispatcher, 'register_sym_predict_proba')


def input_size_from_coef(estimator):
    coef = estimator.coef_
    n_inputs = coef.shape[-1]
    return n_inputs

def input_size_from_n_features_(estimator):
    return estimator.n_features_

def input_size_from_n_features(estimator):
    return estimator.n_features


input_size_doc = '''
Parameters
----------
estimator : A scikit-learn or other compatible fitted estimator.

Returns
-------
int
    The number of columns needed for prediction by estimator.

Raises
------
NotFittedError
    When the estimator is not fitted.

NotImplementedError
    When the estimator's type is not supported.

'''
input_size_dispatcher = {}
input_size = call_method_or_dispatch('input_size', input_size_dispatcher)
register_input_size = create_registerer(input_size_dispatcher, 'register_input_size')

sym_predict_doc = '''
Parameters
----------
estimator : A scikit-learn or other compatible fitted classifier.

Returns
-------
Function
    A Function object specifying the predict function for estimator.

Raises
------
NotFittedError
    When the estimator is not fitted.

NotImplementedError
    When the estimator's type is not supported.

'''
sym_predict_dispatcher = {}
sym_predict = call_method_or_dispatch('sym_predict', sym_predict_dispatcher, docstring=sym_predict_doc)
register_sym_predict = create_registerer(sym_predict_dispatcher, 'register_sym_predict')

sym_score_to_decision_doc = '''
Parameters
----------
loss : A scikit-learn LossFunction or other compatible loss function.

Returns
-------
Function
    A Function object specifying the relationship between score and decision_function for estimator.

Raises
------
NotImplementedError
    When the loss's type is not supported.
'''
sym_score_to_decision_dispatcher = {}
sym_score_to_decision = call_method_or_dispatch('sym_score_to_decision', sym_score_to_decision_dispatcher, docstring=sym_score_to_decision_doc)
register_sym_score_to_decision = create_registerer(sym_score_to_decision_dispatcher, 'register_sym_score_to_decision')


sym_score_to_proba_doc = '''
Parameters
----------
loss : A scikit-learn LossFunction or other compatible loss function.

Returns
-------
Function
    A Function object specifying the relationship between score and predict_proba for estimator.

Raises
------
NotImplementedError
    When the loss's type is not supported.
'''
sym_score_to_proba_dispatcher = {}
sym_score_to_proba = call_method_or_dispatch('sym_score_to_proba', sym_score_to_proba_dispatcher, docstring=sym_score_to_proba_doc)
register_sym_score_to_proba = create_registerer(sym_score_to_proba_dispatcher, 'register_sym_score_to_proba')

sym_transform_doc = '''
Parameters
----------
estimator : A scikit-learn or other compatible fitted classifier.

Returns
-------
Function
    A Function object specifying the transform function for estimator.

Raises
------
NotFittedError
    When the estimator is not fitted.

NotImplementedError
    When the estimator's type is not supported.
'''
sym_transform_dispatcher = {}
sym_transform = call_method_or_dispatch('sym_transform', sym_transform_dispatcher, docstring=sym_transform_doc)
register_sym_transform = create_registerer(sym_transform_dispatcher, 'register_sym_transform')

syms_doc = '''
Parameters
----------
estimator : A scikit-learn or other compatible fitted estimator.

Returns
-------
tuple of Symbols
    The input symbols estimator.

Raises
------
NotFittedError
    When the estimator is not fitted.

NotImplementedError
    When the estimator's type is not supported.
'''
def syms_x(estimator):
    return [Symbol('x%d' % d) for d in range(input_size(estimator))]

syms_dispatcher = {
                   BaseEstimator: syms_x,
                   }
syms = call_method_or_dispatch('syms', syms_dispatcher, docstring=syms_doc)
register_syms = create_registerer(syms_dispatcher, 'register_syms')



        
    
    

