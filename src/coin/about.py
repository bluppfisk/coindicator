from gi.repository import GdkPixbuf, Gtk


class AboutWindow(Gtk.AboutDialog):
    def __init__(self, config):
        super().__init__()
        self.config = config

        logo_124px = GdkPixbuf.Pixbuf.new_from_file(
            self.config.get("project_root") + "/resources/icon_32px.png"
        )
        self.set_program_name(self.config.get("app").get("name"))
        self.set_comments(self.config.get("app").get("description"))
        self.set_version(self.config.get("app").get("version"))
        self.set_website(self.config.get("app").get("url"))
        authors = []
        for author in self.config.get("authors"):
            authors.append("{} <{}>".format(author.get("name"), author.get("email")))

        self.set_authors(authors)
        contributors = []
        for contributor in self.config.get("contributors"):
            contributors.append(
                "{} <{}>".format(contributor.get("name"), contributor.get("email"))
            )
        self.add_credit_section("Exchange plugins", contributors)
        self.set_artists(
            [
                "{} <{}>".format(
                    self.config.get("artist").get("name"),
                    self.config.get("artist").get("email"),
                )
            ]
        )
        self.set_license_type(Gtk.License.MIT_X11)
        self.set_logo(logo_124px)
        self.set_keep_above(True)

    def show(self):
        res = self.run()
        if res == -4 or -6:  # close events
            self.destroy()
