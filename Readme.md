PHP Getters and Setters
=======================

** Partial support for ST3, "generate for ..." is not working **



With PHP Getters and Setters you can automatically generate _Getters_ and _Setters_ for your php classes.
The code generated is compliant with [PSR1][1] and [PSR2][2] Standards



Features:
---------

* Generate Getters, Setters or Both
* Can be applied to all class properties or just to a single one
* DocBlocks included
* Description, Type and Type Hinting automatically discovered from the variable dockblock


**Example PHP Code**


```php
class test
{
    /**
     * foo container
     *
     * @var AbcClass
     */
    private $foo;
}
```

**Example class after generating Getters and Setters**

```php
class test
{
    /**
     * foo container
     *
     * @var AbcClass
     */
    private $foo;

    /**
     * Gets the foo container.
     *
     * @return AbcClass
     */
    public function getFoo()
    {
        return $this->foo;
    }

    /**
     * Sets the foo container.
     *
     * @param AbcClass $foo the foo
     */
    public function setFoo(AbcClass $foo)
    {
        $this->foo = $foo;
    }
}
```

As you can see if get to trouble of commenting your variables, the generated functions can be used without modification.

This is an huge time saver!

Settings Reference
------------------

###templates
_type_   : **string**

_default_: **templates/**

_description_: the path to the templates folder. if you need to change templates you need to copy  _templates/_ folder to another location and do you changes

###style
_type_   : **string**

_default_: **camelCase**

_accepts_: **camelCase | snake_case**

_description_: the coding style, use _camelCase_ for camel case or _snake_case_ for snake case

###type_hint_ignore
_type_: **list of strings**

_default_: **["mixed", "int","integer", "double", "float", "number", "string", "boolean", "bool", "numeric", "unknown"]**

_description_: if the property has one of the types listed type hinting will not be used

###fluent interface
_type_: mixed

accepts_: **true | false | ask**

_default_: **ask**

_description_: whether to generate code supporting a fluent interface or not, default is to ask

[1]: https://github.com/php-fig/fig-standards/blob/master/accepted/PSR-1-basic-coding-standard.md
[2]: https://github.com/php-fig/fig-standards/blob/master/accepted/PSR-2-coding-style-guide.md
