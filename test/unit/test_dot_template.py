from tracardi.context import ServerContext, Context
from tracardi.domain.profile import Profile
from tracardi.common.dot_notation.dot_accessor import DotAccessor
from tracardi.common.template.dot_template import DotTemplate


def test_dot_template():
    with ServerContext(Context(production=False)):
        profile = Profile.new("id")
        profile.traits['none'] = None
        dot = DotAccessor(profile=Profile.new("id"))

        et = DotTemplate()
        assert "xxxx placeholder" == et.render("xxxx placeholder", dot)
        assert "xxxx Template id" == et.render('xxxx {{profile@id ? "Template %s" ! "Render if not value"}}', dot)
        assert "xxxx id" == et.render('xxxx {{profile@id}}', dot)
        assert "xxxx unknown" == et.render('xxxx {{profile@traits.none}}', dot)
        assert "xxxx unknown" == et.render('xxxx {{profile@xxx}}', dot)
        assert "xxxx no data" == et.render('xxxx {{profile@xxx ! "no data"}}', dot)
        assert "xxxx no jest id" == et.render('xxxx {{profile@xxx ! "no"}} {{profile@id ? "jest %s"}}', dot)