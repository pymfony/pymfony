# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""
"""

from __future__ import absolute_import;

import unittest;
import inspect;

from pymfony.component.console.formatter import OutputFormatterStyle;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.console.formatter import OutputFormatterStyleStack;
from pymfony.component.console.formatter import OutputFormatter;

class OutputFormatterStyleTest(unittest.TestCase):

    def testConstructor(self):

        style = OutputFormatterStyle('green', 'black', ['bold', 'underscore']);
        self.assertEqual("\033[32;40;1;4mfoo\033[0m", style.apply('foo'));

        style = OutputFormatterStyle('red', None, ['blink']);
        self.assertEqual("\033[31;5mfoo\033[0m", style.apply('foo'));

        style = OutputFormatterStyle(None, 'white');
        self.assertEqual("\033[47mfoo\033[0m", style.apply('foo'));


    def testForeground(self):

        style = OutputFormatterStyle();

        style.setForeground('black');
        self.assertEqual("\033[30mfoo\033[0m", style.apply('foo'));

        style.setForeground('blue');
        self.assertEqual("\033[34mfoo\033[0m", style.apply('foo'));

        self.assertRaises(InvalidArgumentException, style.setForeground, 'undefined-color');


    def testBackground(self):

        style = OutputFormatterStyle();

        style.setBackground('black');
        self.assertEqual("\033[40mfoo\033[0m", style.apply('foo'));

        style.setBackground('yellow');
        self.assertEqual("\033[43mfoo\033[0m", style.apply('foo'));

        self.assertRaises(InvalidArgumentException, style.setBackground, 'undefined-color');


    def testOptions(self):

        style = OutputFormatterStyle();

        style.setOptions(['reverse', 'conceal']);
        self.assertEqual("\033[7;8mfoo\033[0m", style.apply('foo'));

        style.setOption('bold');
        self.assertEqual("\033[7;8;1mfoo\033[0m", style.apply('foo'));

        style.unsetOption('reverse');
        self.assertEqual("\033[8;1mfoo\033[0m", style.apply('foo'));

        style.setOption('bold');
        self.assertEqual("\033[8;1mfoo\033[0m", style.apply('foo'));

        style.setOptions(['bold']);
        self.assertEqual("\033[1mfoo\033[0m", style.apply('foo'));


class OutputFormatterStyleStackTest(unittest.TestCase):

    def testPush(self):

        stack = OutputFormatterStyleStack();
        s1 = OutputFormatterStyle('white', 'black');
        stack.push(s1);
        s2 = OutputFormatterStyle('yellow', 'blue');
        stack.push(s2);

        self.assertEqual(s2, stack.getCurrent());

        s3 = OutputFormatterStyle('green', 'red');
        stack.push(s3);

        self.assertEqual(s3, stack.getCurrent());


    def testPop(self):

        stack = OutputFormatterStyleStack();
        s1 = OutputFormatterStyle('white', 'black');
        stack.push(s1);
        s2 = OutputFormatterStyle('yellow', 'blue');
        stack.push(s2);

        self.assertEqual(s2, stack.pop());
        self.assertEqual(s1, stack.pop());


    def testPopEmpty(self):

        stack = OutputFormatterStyleStack();
        style = OutputFormatterStyle();

        actual = stack.pop()
        for var in dir(style):
            vactual = getattr(actual, var);
            vexpected = getattr(style, var);
            if not inspect.ismethod(vexpected) and not str(var).endswith('__'):
                self.assertEqual(vexpected, vactual);


    def testPopNotLast(self):

        stack = OutputFormatterStyleStack();
        s1 = OutputFormatterStyle('white', 'black');
        stack.push(s1);
        s2 = OutputFormatterStyle('yellow', 'blue');
        stack.push(s2);
        s3 = OutputFormatterStyle('green', 'red');
        stack.push(s3);

        self.assertEqual(s2, stack.pop(s2));
        self.assertEqual(s1, stack.pop());


    def testInvalidPop(self):
        """@expectedException InvalidArgumentException

        """

        def execut():
            stack = OutputFormatterStyleStack();
            stack.push(OutputFormatterStyle('white', 'black'));
            stack.pop(OutputFormatterStyle('yellow', 'blue'));

        self.assertRaises(InvalidArgumentException, execut);


class FormatterStyleTest(unittest.TestCase):

    def testEmptyTag(self):

        formatter = OutputFormatter(True);
        self.assertEqual("foo<>bar", formatter.format('foo<>bar'));


    def testLGCharEscaping(self):

        formatter = OutputFormatter(True);

        self.assertEqual("foo<bar", formatter.format('foo\\<bar'));
        self.assertEqual("<info>some info</info>", formatter.format('\\<info>some info\\</info>'));
        self.assertEqual("\\<info>some info\\</info>", OutputFormatter.escape('<info>some info</info>'));

        self.assertEqual(
            "\033[33mSymfony\\Component\\Console does work very well!\033[0m",
            formatter.format('<comment>Symfony\Component\Console does work very well!</comment>')
        );


    def testBundledStyles(self):

        formatter = OutputFormatter(True);

        self.assertTrue(formatter.hasStyle('error'));
        self.assertTrue(formatter.hasStyle('info'));
        self.assertTrue(formatter.hasStyle('comment'));
        self.assertTrue(formatter.hasStyle('question'));

        self.assertEqual(
            "\033[37;41msome error\033[0m",
            formatter.format('<error>some error</error>')
        );
        self.assertEqual(
            "\033[32msome info\033[0m",
            formatter.format('<info>some info</info>')
        );
        self.assertEqual(
            "\033[33msome comment\033[0m",
            formatter.format('<comment>some comment</comment>')
        );
        self.assertEqual(
            "\033[30;46msome question\033[0m",
            formatter.format('<question>some question</question>')
        );


    def testNestedStyles(self):

        formatter = OutputFormatter(True);

        self.assertEqual(
            "\033[37;41msome \033[0m\033[32msome info\033[0m\033[37;41m error\033[0m",
            formatter.format('<error>some <info>some info</info> error</error>')
        );


    def testStyleMatchingNotGreedy(self):

        formatter = OutputFormatter(True);

        self.assertEqual(
            "(\033[32m>=2.0,<2.3\033[0m)",
            formatter.format('(<info>>=2.0,<2.3</info>)')
        );


    def testStyleEscaping(self):

        formatter = OutputFormatter(True);

        self.assertEqual(
            "(\033[32mz>=2.0,<a2.3\033[0m)",
            formatter.format('(<info>'+formatter.escape('z>=2.0,<a2.3')+'</info>)')
        );


    def testDeepNestedStyles(self):

        formatter = OutputFormatter(True);

        self.assertEqual(
            "\033[37;41merror\033[0m\033[32minfo\033[0m\033[33mcomment\033[0m\033[37;41merror\033[0m",
            formatter.format('<error>error<info>info<comment>comment</info>error</error>')
        );


    def testNewStyle(self):

        formatter = OutputFormatter(True);

        style = OutputFormatterStyle('blue', 'white');
        formatter.setStyle('test', style);

        self.assertEqual(style, formatter.getStyle('test'));
        self.assertNotEqual(style, formatter.getStyle('info'));

        self.assertEqual("\033[34;47msome custom msg\033[0m", formatter.format('<test>some custom msg</test>'));


    def testRedefineStyle(self):

        formatter = OutputFormatter(True);

        style = OutputFormatterStyle('blue', 'white');
        formatter.setStyle('info', style);

        self.assertEqual("\033[34;47msome custom msg\033[0m", formatter.format('<info>some custom msg</info>'));


    def testInlineStyle(self):

        formatter = OutputFormatter(True);

        self.assertEqual("\033[34;41msome text\033[0m", formatter.format('<fg=blue;bg=red>some text</>'));
        self.assertEqual("\033[34;41msome text\033[0m", formatter.format('<fg=blue;bg=red>some text</fg=blue;bg=red>'));


    def testNonStyleTag(self):

        formatter = OutputFormatter(True);
        self.assertEqual("\033[32msome \033[0m\033[32m<tag> styled\033[0m", formatter.format('<info>some <tag> styled</info>'));


    def testNotDecoratedFormatter(self):

        formatter = OutputFormatter(False);

        self.assertTrue(formatter.hasStyle('error'));
        self.assertTrue(formatter.hasStyle('info'));
        self.assertTrue(formatter.hasStyle('comment'));
        self.assertTrue(formatter.hasStyle('question'));

        self.assertEqual(
            "some error", formatter.format('<error>some error</error>')
        );
        self.assertEqual(
            "some info", formatter.format('<info>some info</info>')
        );
        self.assertEqual(
            "some comment", formatter.format('<comment>some comment</comment>')
        );
        self.assertEqual(
            "some question", formatter.format('<question>some question</question>')
        );

        formatter.setDecorated(True);

        self.assertEqual(
            "\033[37;41msome error\033[0m", formatter.format('<error>some error</error>')
        );
        self.assertEqual(
            "\033[32msome info\033[0m", formatter.format('<info>some info</info>')
        );
        self.assertEqual(
            "\033[33msome comment\033[0m", formatter.format('<comment>some comment</comment>')
        );
        self.assertEqual(
            "\033[30;46msome question\033[0m", formatter.format('<question>some question</question>')
        );


    def testContentWithLineBreaks(self):

        formatter = OutputFormatter(True);

        self.assertEqual("""
\033[32m
some text\033[0m
"""
            , formatter.format("""
<info>
some text</info>
"""
        ));

        self.assertEqual("""
\033[32msome text
\033[0m
"""
            , formatter.format("""
<info>some text
</info>
"""
        ));

        self.assertEqual("""
\033[32m
some text
\033[0m
"""
            , formatter.format("""
<info>
some text
</info>
"""
        ));

        self.assertEqual("""
\033[32m
some text
more text
\033[0m
"""
            , formatter.format("""
<info>
some text
more text
</info>
"""
        ));


if __name__ == '__main__':
    unittest.main();
