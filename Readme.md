PHP Getters and Setters
=======================


With PHP Getters and Setters you can automatically generate _Getters_ and _Setters_ for your php classes.

Features:
---------

* Generate Getters, Setters or Both
* Can be applied to all class properties or just to a single one
* Description, Type and Type Hinting automatically discovered from the variable dockblock
* fully customizable templates


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

Usage
-----

Commands available are:

 * Generate Getters and Setters
 * Generate Getter
 * Generate Setter
 * Generate Getter for...
 * Generate Setter for...

These can be accesed via the context menu (right click on the source of any open PHP file) or the command pallette. The currently open file *must* be a PHP file.

Settings Reference
------------------

###registerTemplates
_type_   : **array**

_default_: **[]**

_description_: the user templates to load

###template
_type_   : **string**

_default_: **camelCaseFluent**

_description_: the template to use

###type_hint_ignore
_type_: **list of strings**

_default_: **["mixed", "int","integer", "double", "float", "number", "string", "boolean", "bool", "numeric", "unknown"]**

_description_: if the property has one of the types listed type hinting will not be used


Creating your own template
--------------------------
create a file named ```user_templates.py``` in ```<packages folder>/PHP Getters and Setters/```

example template:
```python
class camelCase(object):
    name = "camelCase"
    style = 'camelCase' # can also be snakeCase
    getter = """
/**
* Gets the %(description)s.
*
* @return %(type)s
*/
public function get%(normalizedName)s()
{
    return $this->%(name)s;
}
"""

    setter = """
/**
* Sets the %(description)s.
*
* @param %(type)s $%(name)s the %(humanName)s
*
* @return self
*/
public function set%(normalizedName)s(%(typeHint)s $%(name)s)
{
    $this->%(name)s = $%(name)s;
}
"""
```
