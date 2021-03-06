import logging
from datetime import datetime
from time import sleep

from praw import Reddit as RedditApi

from db.mongo import RedditDatabase

from commons.classes import Singleton
from commons.classes import Submission

from commons.settings import REDDIT_CLIENTID
from commons.settings import REDDIT_CLIENTSECRET
from commons.settings import REDDIT_PASSWORD
from commons.settings import REDDIT_USERAGENT
from commons.settings import REDDIT_USERNAME


LOG = logging.getLogger('reddit')

FLAIRS = {
    '3ds': 'Sale',
    '3dsdeals': 'Digital Download',
    'nintendoswitch': 'Sale',
    'nintendoswitchdeals': 'Digital Download',
}


class Reddit(metaclass=Singleton):

    def __init__(self):
        self.api = RedditApi(
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            client_id=REDDIT_CLIENTID,
            client_secret=REDDIT_CLIENTSECRET,
            user_agent=REDDIT_USERAGENT
        )

    def inbox(self):
        return [message for message in self.api.inbox.unread() if not message.was_comment]

    def send(self, username, title, content):
        try:
            LOG.info('Sending to {}: {}'.format(username, title))

            self.api.redditor(username).message(title, content)
            sleep(10)
        except:
            LOG.error('Error sending to {}: {}'.format(username, title))

    def reply(self, message, content):
        try:
            LOG.info('Replying to {}: {}'.format(message.author.name, message.subject))

            message.reply(content)
            message.mark_read()
            sleep(10)
        except:
            LOG.error('Error replying to {}: {}'.format(message.author.name, message.subject))

    def usable(self, sub, country=None):
        if not sub:
            return False

        now = datetime.utcnow()

        try:
            submission = self.api.submission(id=sub.submission_id)

            if not submission.author or submission.author.name != REDDIT_USERNAME:
                LOG.info(f'Submission was deleted: {sub}')
                return False
            else:
                LOG.info(f'Submission wasnt deleted: {sub}')

            if submission.stickied and (now - sub.created_at).days < 170:
                LOG.info(f'Submission is stickied and not expired: {sub}')
                return True
            else:
                LOG.info(f'Submission isnt stickied or expired: {sub}')

            if now > sub.expires_at:
                LOG.info(f'Submission expired: {sub}')
                return False
            else:
                LOG.info(f'Submission is active: {sub}')

                if country:
                    LOG.info(f'Submission is for a country, it will be reused: {sub}')
                    return True

            if now.today().weekday() not in [0, 3]:  # now is not monday/thursday
                LOG.info(f'Submission will be reused (not monday/thursday yet): {sub}')
                return True
            else:
                LOG.info(f'Submission might be replaced (monday/thursday): {sub}')

            if now.hour < 18:
                LOG.info(f'Submission will be reused (not 18:00 UTC yet): {sub}')
                return True
            else:
                LOG.info(f'Submission might be replaced (18:00 UTC): {sub}')

            if sub.created_at.day != now.day:
                LOG.info(f'Submission will be replaced (it\'s monday/thursday, my dudes): {sub}')
                return False
            else:
                LOG.info(f'Submission wont be replaced (already created one today): {sub}')

        except Exception as e:
            LOG.error(f'Submission shows error {str(e)}, will be replaced: {sub}')
            return False

        LOG.info(f'Submission will be reused: {sub}')
        return True

    def create(self, subreddit, title, content):
        submission = self.api\
            .subreddit(subreddit)\
            .submit(title, selftext=content)

        submission.disable_inbox_replies()

        self.update_flair(submission, subreddit)

        return submission.id

    def edit(self, sub, content):
        submission = self.api.submission(id=sub.submission_id)

        if not submission:
            return

        submission.edit(content)
        LOG.info(f'Submission updated: {sub}')

    def nsfw(self, sub):
        if not sub:
            return

        submission = self.api.submission(id=sub.submission_id)

        if not submission:
            return

        try:
            submission.mod.nsfw()
            LOG.info(f'Submission marked as NSFW: {sub}')
        except:
            LOG.error(f'Submission can\'t be marked as NSFW: {sub}')

    def update_flair(self, submission, subreddit):
        try:
            flair_text = FLAIRS.get(subreddit)

            if not flair_text:
                return
            else:
                flair_text = flair_text.lower()

            for flair in submission.flair.choices():
                if flair['flair_text'].lower() == flair_text:
                    submission.flair.select(flair['flair_template_id'])

                    LOG.info(f'Flair "{flair_text}" applied')
                    break
            else:
                LOG.warning(f'Flair "{flair_text}" not found for {subreddit}')
        except Exception as e:
            LOG.error(f'Flair for "{subreddit}" can\'t applied: {str(e)}')

    def submit(self, system, subreddit, title, content, country=None):
        subreddit = subreddit.lower()

        reddit_db = RedditDatabase()

        key = f'{system}/{country if country else subreddit}'
        sub = reddit_db.load(key)

        now = datetime.utcnow()

        if not self.usable(sub, country):
            self.nsfw(sub)

            sub = Submission(
                _id=key,
                submission_id=self.create(subreddit, title, content),
                subreddit=subreddit,
                system=system,
                title=title,
                days_to_expire=14 if country else 165
            )

            LOG.info(f'Submission created: {sub}')
        else:
            self.edit(sub, content)
            sub.updated_at = now

        reddit_db.save(sub)

        sleep(5)

        return sub

