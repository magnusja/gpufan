from nvfan.curve import Curve
import sure


def test_curve_creation():
    curve = Curve()
    curve.evaluate(30).should.equal(30)
    curve.evaluate(68).should.equal(65)


def test_curve_points():
    curve = Curve([[30, 30], [100, 100]])
    curve.evaluate(90).should.equal(90)

    curve = Curve([[30, 30], [60, 60]])
    curve.evaluate(86).should.equal(None)
