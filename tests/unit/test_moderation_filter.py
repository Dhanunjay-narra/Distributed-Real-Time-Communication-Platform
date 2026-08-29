from packages.moderation.filter import ContentFilter

def test_content_moderation_filter():
    cfilter = ContentFilter()
    res_clean = cfilter.evaluate_message("Hello team, meet you at 3pm.")
    assert res_clean["is_flagged"] is False
    
    res_flag = cfilter.evaluate_message("Click here to win free prizes from phishing link.")
    assert res_flag["is_flagged"] is True
