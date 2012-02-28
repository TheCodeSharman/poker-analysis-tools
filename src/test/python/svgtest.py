import unittest

from gui.svg.svgreader import *

class Test(unittest.TestCase):
    def testNumber1(self):
        self.assertEqual( number.parseString( "123" ).asList(), [ 123 ])
    def testNumber2(self):
        self.assertEqual( number.parseString( "+123" ).asList(), [ 123 ])
    def testNumber3(self):
        self.assertEqual( number.parseString( "-123" ).asList(), [-123 ])
    def testNumber4(self):
        self.assertEqual( number.parseString( "-123.456" ).asList(), [ -123.456 ])
    def testNumber5(self):
        self.assertEqual( number.parseString( "-.456" ).asList(), [ -0.456 ])
        
    def testTransformMatrix(self):
        self.assertEqual( transform.parseString( "matrix( 1.1,2.2,3.3,4.4,5.5,6.6 )")[0], SvgMatrix( 1.1, 2.2, 3.3, 4.4, 5.5, 6.6 ) )
    def testTransformTranslate(self):
        self.assertEqual( transform.parseString( "translate( 1.1,2.2 )")[0], SvgTranslate( 1.1, 2.2 ) )
    def testTransformScale(self):
        self.assertEqual( transform.parseString( "scale( 1.1, 2.2 )")[0], SvgScale( 1.1, 2.2 ) )
    def testTransformRotate(self):
        self.assertEqual( transform.parseString( "rotate( 130.0,1.1,2.2 )")[0], SvgRotate( 130.0, 1.1, 2.2 ) )
    def testTransformSkewX(self):
        self.assertEqual( transform.parseString( "skewX( 130.0 )")[0], SvgSkewX( 130.0 ) )
    def testTransformSkewY(self):
        self.assertEqual( transform.parseString( "skewY( 130.0 )")[0], SvgSkewY( 130.0 ) )
    def testTransformList(self):
        self.assertEqual( transformList.parseString( "skewY( 130.0 ), rotate( 130.0,1.1,2.2 )").asList(), [ SvgSkewY( 130.0 ), SvgRotate( 130.0, 1.1, 2.2 ) ] )

    def testPathCommand1(self):
        self.assertEqual( parsePathCommand('M 100,200'), [ ['M', 100, 200] ])
        
    def testPathCommand2(self):
        self.assertEqual( parsePathCommand('m -1016.046,25.720671 -10.7642,16.120541 7.1773,18.006272 -18.6578,-5.255841 -14.9071,12.390288 -0.767,-19.36883 -16.3904,-10.348653 18.1838,-6.714754 4.7773,-18.786107 12.0052,15.218884 z'), 
                          [ ['m', -1016.046,25.720671, -10.7642,16.120541, 7.1773,18.006272, -18.6578,-5.255841, -14.9071,12.390288, -0.767,-19.36883, -16.3904,-10.348653, 18.1838,-6.714754, 4.7773,-18.786107, 12.0052,15.218884], ['z']])