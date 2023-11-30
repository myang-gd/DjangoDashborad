# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
from common_utils.constant import Constant, ResponseType, ValidationType
from common_utils.json_util import JsonUtil
import  re
VALIDATION, AND, OR, NOT, LPAREN, RPAREN, EOF = (
    'VALIDATION', '&&', '||', '!(', '(', ')', 'EOF'
)
NOTNULL_VALIDATION ='! ( ' + Constant.NULL + ' )'
class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __str__(self):
        """String representation of the class instance.

        Examples:
            Token(AND, '&&')
            Token(VALIDATION, 'test')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


class Lexer(object):
    def __init__(self, text):
        # client string input, e.g. "4 + 2 * 3 - 6 / 2"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]
    def error(self):
        raise Exception('Invalid character')

    def advance(self, length=1):
        """Advance the `pos` pointer and set the `current_char` variable."""
        moved_length = 0
        while moved_length < length:
            self.pos += 1
            if self.pos > len(self.text) - 1:
                self.current_char = None  # Indicates end of input
            else:
                self.current_char = self.text[self.pos]
            moved_length += 1
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def validation(self):
        """Return a (multichar) string consumed from the input."""
        result = ''
        while self.current_char is not None and self.isVaidation():
            result += self.current_char
            self.advance()
        return str(result)
    def isVaidation(self):
        if self.current_char in(LPAREN, RPAREN) or self.get_current_chars() in (AND, OR, NOT):
            return False
        else: 
            return True 
    def get_current_chars(self, length=2):    
        current_chars = ''
        pos = self.pos
        while pos <= len(self.text) - 1 and len(current_chars) < length:
            current_chars += self.text[pos]
            pos += 1
        return current_chars
    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.isVaidation():
                next_token =  Token(VALIDATION, self.validation());
                if next_token.value.strip() == '':
                    next_token = self.get_next_token()
                return next_token
            if self.get_current_chars() == AND:
                self.advance(length=2)
                return Token(AND, '&&')
            if self.get_current_chars() == OR:
                self.advance(length=2)
                return Token(OR, '||')
            if self.get_current_chars() == NOT:
                self.advance(length=2)
                return Token(NOT, '!(')
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            self.error()

        return Token(EOF, None)


class Interpreter(object):
    def __init__(self, lexer, response, responseType:ResponseType, **kwargs):
        self.lexer = lexer
        self.response = response
        self.json_response = JsonUtil.safe_loads(response)
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()
        self.validation_result_map = {}
        self.responseType = responseType
        self.validationTypeEnum = ValidationType.toEnum(kwargs.get('validationType'))
    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()
    def isEmpty(self, response):
        return (response is None or response == '' or response == '[]')
    def isContains(self, validation, isNot):           
        if self.json_response and self.responseType != ResponseType.plain:
            return self.isContains_json_response(validation, isNot)
        elif self.response:
            return self.isContains_plain_response(validation, isNot, isResponseNull=self.isEmpty(self.response))
        elif not self.response:
            return self.isContains_plain_response(validation, isNot, isResponseNull=True)
    def isMatch(self, actual, expected, validationType:ValidationType):
        if validationType == ValidationType.regex:
            return re.compile(expected).match(actual) != None
        else:
            return actual == expected
    def isMatchContain(self, actual, expected, validationType:ValidationType):
        if validationType == ValidationType.regex:
            return re.compile(expected,  re.MULTILINE|re.DOTALL).match(actual) != None
        else:
            return expected in actual
    def isContains_null(self, validation, isNot, isResponseNull=False):
            if not isResponseNull:
                if isNot:
                    self.validation_result_map[NOTNULL_VALIDATION] = { Constant.EXPECTED: Constant.NOT_EMPTY, Constant.RESULT: Constant.PASSED, Constant.ACTUAL:Constant.NOT_EMPTY}
                    return False # outer !( will return true
                else:
                    self.validation_result_map[Constant.NULL] = { Constant.EXPECTED: Constant.EMPTY, Constant.RESULT: Constant.FAILED, Constant.ACTUAL:Constant.NOT_EMPTY}
                    return False
            else:
                if isNot:
                    self.validation_result_map[NOTNULL_VALIDATION] = { Constant.EXPECTED: Constant.NOT_EMPTY, Constant.RESULT: Constant.FAILED, Constant.ACTUAL:Constant.EMPTY}
                    return True
                else:
                    self.validation_result_map[Constant.NULL] = { Constant.EXPECTED: Constant.EMPTY, Constant.RESULT: Constant.PASSED, Constant.ACTUAL:Constant.EMPTY}
                    return True
    def isContains_json_response(self, validation, isNot):
        if validation.strip().upper() == Constant.NULL:
            validation = Constant.EMPTY
            return self.isContains_null(validation, isNot)            
        if self.responseType == ResponseType.key_value:
            actualList, expected, validation_new = JsonUtil.getActualAndExpectedForKeyValue(validation, self.json_response)  
        else:
            actualList, expected, validation_new = JsonUtil.getActualAndExpected(validation, self.json_response) 
       
        if actualList:
            is_equal = True
        else:
            is_equal = False 
        for actual in actualList:
            is_equal = (self.isMatch(actual, expected, self.validationTypeEnum)  and is_equal) 
        
        if isNot:
            validation_new = '! ( ' +validation_new + ' )'
            result_str = (Constant.PASSED if not is_equal else Constant.FAILED)
        else:
            result_str = (Constant.PASSED if is_equal else Constant.FAILED)
        result_map = {}
        result_map[Constant.EXPECTED] = expected
        result_map[Constant.RESULT] = result_str
        result_map[Constant.ACTUAL] = ', '.join(actualList)
        self.validation_result_map[validation_new] = result_map 
        return is_equal 
    
    def isContains_plain_response(self, validation, isNot, isResponseNull=False):
        if validation.strip().upper() == Constant.NULL:
            validation = Constant.EMPTY
            return self.isContains_null(validation, isNot, isResponseNull=isResponseNull)     
        isContain = (True if validation.strip().upper() == Constant.NULL and self.isEmpty(self.response)  else self.isMatchContain(self.response, validation.strip(), self.validationTypeEnum))
        if isNot:
            self.validation_result_map['! ( ' + validation + ' )'] = (Constant.PASSED if not isContain else Constant.FAILED)
        else:
            self.validation_result_map[validation] = (Constant.PASSED if isContain else Constant.FAILED)
        return isContain
    def factor(self, Not=False):
        """factor : VALIDATION | LPAREN VALIDATION RPAREN | NOT VALIDATION RPAREN"""
        token = self.current_token
        if token.type == VALIDATION:
            self.eat(VALIDATION)
            return self.isContains(token.value, Not)
        elif token.type == NOT:
            self.eat(NOT)
            result = self.expr(Not = (not Not))
            self.eat(RPAREN)
            return not result
        elif token.type == LPAREN:
            self.eat(LPAREN)
            result = self.expr(Not = Not)
            self.eat(RPAREN)
            return result
    def clear_vaditions(self, result:bool):
        if not self.validation_result_map:
            return
        if result:
            self.remove_null_validation()
        else:
            failed_none_null_validation = next((validation for validation, validation_result in self.validation_result_map.items() if type(validation_result) is dict and validation_result[Constant.RESULT] == str(Constant.FAILED) and validation != Constant.NULL and validation != NOTNULL_VALIDATION), None)
            if failed_none_null_validation:
                self.remove_null_validation()    
    def remove_null_validation(self):   
        if Constant.NULL in self.validation_result_map:
            self.validation_result_map.pop(Constant.NULL) 
        if NOTNULL_VALIDATION in self.validation_result_map:
            self.validation_result_map.pop(NOTNULL_VALIDATION)      
    def expr(self, Not=False):
        """logic expression parser / interpreter.
        expr   : term ((PLUS | MINUS) term)*
        factor : VALIDATION | LPAREN VALIDATION RPAREN | NOT VALIDATION RPAREN
        """
        result = self.factor(Not=Not)
 
        while self.current_token.type in (AND, OR):
            token = self.current_token
            if token.type == AND:
                self.eat(AND)
                factor = self.factor(Not=Not)
                result = (result and factor)
            elif token.type == OR:
                self.eat(OR)
                factor = self.factor(Not=Not)
                result = (result or factor)
        
        return result
