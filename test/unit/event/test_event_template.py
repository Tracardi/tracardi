from tracardi.service.notation.event_description_template import EventDescriptionTemplate


def test_event_template():
    et = EventDescriptionTemplate()
    assert "xxxx placeholder" == et.render("xxxx placeholder", {"placeholder": "value"})
    assert "xxxx Template value" == et.render('xxxx {{placeholder ? "Template %s" ! "Render if not value"}}', {"placeholder": "value"})
    assert "xxxx value" == et.render('xxxx {{placeholder}}', {"placeholder": "value"})
    assert "xxxx unknown" == et.render('xxxx {{placeholder1}}', {"placeholder": "value"})
    assert "xxxx no" == et.render('xxxx {{placeholder1 ! "no"}}', {"placeholder": "value"})
    assert "xxxx no jest value" == et.render('xxxx {{placeholder1 ! "no"}} {{placeholder ? "jest %s"}}', {"placeholder": "value"})