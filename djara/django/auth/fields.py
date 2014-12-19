from arangodb.orm.fields import CharField
from django.contrib.auth.hashers import PBKDF2SHA1PasswordHasher

hasher = PBKDF2SHA1PasswordHasher()


class PasswordField(CharField):

    def get(self):
        """
        """

        return self

    def on_save(self, model_instance):
        """
        """

        # Check if the password is not already hashed
        if not '$' in self.text:
            salt = hasher.salt()
            self.text = '%s' % ( hasher.encode(password=self.text, salt=salt, iterations=12000) )

    def verify(self, password):
        hashed_password = self.text
        return hasher.verify(password=password, encoded=hashed_password)