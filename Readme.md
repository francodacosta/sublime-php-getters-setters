PHP Getters and Setters
=======================

With PHP Getters and Setters you can automatically generate _Getters_ and _Setters_ for your php classes.
The code generated is compliant with [PSR1][1] and [PSR2][2] Standards



Features:
---------

* Generate Getters, Setters or Both
* DocBlocks included
* Description, type and Type Hinting automatically discovered from the variable dockblock


Example PHP Code
----------------

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

Example PHP Getters and Setters Generation

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

As you can see if get to trouble of commenting your variables, the generated function can be used without modification.

This is an huge time saver

[1]: https://github.com/php-fig/fig-standards/blob/master/accepted/PSR-1-basic-coding-standard.md
[2]: https://github.com/php-fig/fig-standards/blob/master/accepted/PSR-2-coding-style-guide.md