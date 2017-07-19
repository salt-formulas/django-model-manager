from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):

    def create_user(self, username, email=None, password=None, **kwargs):
        """
        Creates and saves a User with the given email and password.
        if not email:
            raise ValueError('Users must have an email address')
        """

        user = self.model(
            username=(username or self.normalize_email(email)),
            email=self.normalize_email(email),
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create(self, **kwargs):
        return self.create_user(**kwargs)

    def create_superuser(self, username, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username,
            password=password
        )
        user.is_admin = True
        # admin is operator
        user.operator = True
        user.save(using=self._db)
        return user

    def all_operators(self):
        return self.filter(operator=True)

    def all_managers(self):
        return self.filter(manager=True)

    def all_operators_emails(self):
        return [u.email for u in self.all_operators()]


@python_2_unicode_compatible
class Organisation(models.Model):

    name = models.CharField(u"name", max_length=255)
    operator = models.BooleanField(default=False)

    def get_all_operators(self):
        '''obsolete use get_operators'''
        return self.get_operators()

    def get_all_operators_emails(self):
        '''obsolete use get_operators_emails'''
        return self.get_operators_emails()

    def get_operators(self):
        '''returns operators only'''
        return User.objects.all_operators()

    def get_managers(self):
        '''returns managers only'''
        return User.objects.all_managers()

    def get_manager_emails(self):
        '''returns managers emails as simple array'''
        return [u.email for u in self.get_all_operators()]

    def get_operators_emails(self):
        '''returns operators emails as simple array'''
        return [u.email for u in self.get_all_operators()]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "organisation"
        verbose_name_plural = "organisations"


@python_2_unicode_compatible
class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        null=True,
        blank=True
    )
    username = models.CharField(max_length=40, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    enabled = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    organisation = models.ForeignKey(Organisation, blank=True, null=True)
    operator = models.BooleanField(default=False)
    manager = models.BooleanField(default=False)
    phone = models.CharField(max_length=40, blank=True, null=True)

    key_account = models.ManyToManyField(Organisation, blank=True, null=True,
                                         verbose_name=_('Operators organisations'), related_name='operators')

    objects = UserManager()

    USERNAME_FIELD = 'username'

    #REQUIRED_FIELDS = []

    @property
    def manage_organisations(self):
        """restrict operator flag for key_accounts
        """
        if self.is_operator:
            return self.key_account.all()
        return []

    @property
    def is_operator(self):
        """Evaluates whether this user has operator privileges.

        Returns ``True`` or ``False``.
        """

        return self.operator

    @property
    def is_manager(self):
        return self.manager

    def save(self, *args, **kwargs):
        if self.organisation and self.organisation.operator:
            self.operator = True
        super(User, self).save(*args, **kwargs)

    @property
    def organisation_name(self):
        return self.organisation.name

    def get_full_name(self):
        # The user is identified by their email address
        return self.username

    def get_short_name(self):
        # The user is identified by their email address
        return self.username

    def __str__(self):              # __unicode__ on Python 2
        if self.first_name and self.last_name:
            return "%s %s" % (self.first_name, self.last_name)
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All operators are staff
        return (self.operator or self.manager)

    class Meta:
        verbose_name = u"user"
        verbose_name_plural = u"users"

