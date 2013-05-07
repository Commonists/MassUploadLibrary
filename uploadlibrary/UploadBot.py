import re
import pywikibot
import pywikibot.textlib as textlib
from scripts.upload import UploadRobot
from scripts.data_ingestion import DataIngestionBot


class DataIngestionBot(DataIngestionBot):

    def _doUpload(self, photo):
        duplicates = photo.findDuplicateImages(self.site)
        if duplicates:
            pywikibot.output(u"Skipping duplicate of %r" % (duplicates, ))
            return duplicates[0]

        title = cleanUpTitle(photo.getTitle(self.titlefmt))

        description = textlib.glue_template_and_params((self.pagefmt,
                                                        photo.metadata))

        bot = upload.UploadRobot(url=photo.URL,
                                 description=description,
                                 useFilename=title,
                                 keepFilename=True,
                                 verifyDescription=True,
                                 uploadByUrl=False,
                                 targetSite=self.site)
        bot._contents = photo.downloadPhoto().getvalue()
        bot._retrieved = True

        print title
        print description
        bot.run()

        return title

    def _debug_description(self, photo):
        title = cleanUpTitle(photo.getTitle(self.titlefmt))
        description = textlib.glue_template_and_params((self.pagefmt,
                                                        photo.metadata))
        print "= %s =" % title
        print "{{collapse|title=%s|1=<pre>\n%s\n</pre>}}" % (title,
                                                             description)
        print description

    def dry_run(self):
        for photo in self.reader:
            self._debug_description(photo)


def cleanUpTitle(title):
    """Clean up the title of a potential mediawiki page.

    Otherwise the title of the page might not be allowed by the software.

    """

    title = title.strip()
    title = re.sub(u"[<{\\[]", u"(", title)
    title = re.sub(u"[>}\\]]", u")", title)
    title = re.sub(u"[ _]?\\(!\\)", u"", title)
    title = re.sub(u",:[ _]", u", ", title)
    title = re.sub(u"[;:][ _]", u", ", title)
    title = re.sub(u"[\t\n ]+", u" ", title)
    title = re.sub(u"[\r\n ]+", u" ", title)
    title = re.sub(u"[\n]+", u"", title)
    title = re.sub(u"[?!]([.\"]|$)", u"\\1", title)
    title = re.sub(u"[&#%?!]", u"^", title)
    title = re.sub(u"[;]", u",", title)
    title = re.sub(u"[/+\\\\:]", u"-", title)
    title = re.sub(u"--+", u"-", title)
    title = re.sub(u",,+", u",", title)
    title = re.sub(u"[-,^]([.]|$)", u"\\1", title)
    title = title.replace(u" ", u"_")
    return title
