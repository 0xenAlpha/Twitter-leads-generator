class Twitter:
    username_input='//input[@autocapitalize="sentences"]'
    password_input = '//input[@name="password"]'
    next_btn= '//span[text()="Next"]'
    login_btn= '//span[text()="Log in"]'
    followers_tb='//a[contains(@href,"followers")]'
    message_input='//div[@data-testid="dmComposerTextInput"]'
    message_btn = '//div[@aria-label="Send"]'
    message_btn_profile = '//div[@aria-label="Message"]'
    profile_span='//span[text()="Profile"]'
    followers_flow='//div[@aria-label="Timeline: Followers"]'
    reply_btn = '//article[not(descendant::text()=" Retweeted")]//div[@data-testid="reply"]'
    reply_input = '//div[@class="DraftEditor-editorContainer"]/div'
    reply_btn_final = '//span[text()="Reply"]'