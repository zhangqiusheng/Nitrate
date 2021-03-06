# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime

import factory

from factory.django import DjangoModelFactory

from tcms.management.models import Priority
from tcms.testcases.models import TestCaseStatus
from tcms.testcases.models import TestCaseBugSystem
from tcms.testruns.models import TestCaseRunStatus


def md5_hash(s):
    """Helper method returning md5 hash"""
    md5 = hashlib.md5()
    md5.update(s)
    return md5.hexdigest()


# ### Factories for app management ###


class UserFactory(DjangoModelFactory):

    class Meta:
        model = 'auth.User'

    username = factory.Sequence(lambda n: 'User%d' % n)
    email = factory.LazyAttribute(lambda user: '%s@example.com' % user.username)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for group in extracted:
                self.groups.add(group)


class GroupFactory(DjangoModelFactory):

    class Meta:
        model = 'auth.Group'

    name = factory.Sequence(lambda n: 'Group %d' % n)


# ### Factories for app management ###


class ClassificationFactory(DjangoModelFactory):

    class Meta:
        model = 'management.Classification'

    name = factory.Sequence(lambda n: 'Classification %d' % n)


class ProductFactory(DjangoModelFactory):

    class Meta:
        model = 'management.Product'

    name = factory.Sequence(lambda n: 'Product %d' % n)
    classification = factory.SubFactory(ClassificationFactory)


class PriorityFactory(DjangoModelFactory):

    class Meta:
        model = 'management.Priority'

    value = factory.Sequence(lambda n: 'P%d' % n)
    is_active = True


class MilestoneFactory(DjangoModelFactory):

    class Meta:
        model = 'management.Milestone'

    product = factory.SubFactory(ProductFactory)
    value = factory.Sequence(lambda n: 'Milestone %d' % n)


class ComponentFactory(DjangoModelFactory):

    class Meta:
        model = 'management.Component'

    name = factory.Sequence(lambda n: 'Component %d' % n)
    product = factory.SubFactory(ProductFactory)
    initial_owner = factory.SubFactory(UserFactory)
    initial_qa_contact = factory.SubFactory(UserFactory)


class VersionFactory(DjangoModelFactory):

    class Meta:
        model = 'management.Version'

    value = factory.Sequence(lambda n: '0.%d' % n)
    product = factory.SubFactory(ProductFactory)


class TestBuildFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TestBuild'

    name = factory.Sequence(lambda n: 'Build %d' % n)
    product = factory.SubFactory(ProductFactory)


class TestEnvironmentFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TestEnvironment'

    name = factory.Sequence(lambda n: 'Environment %d' % n)
    product = factory.SubFactory(ProductFactory)


class TestEnvironmentCategoryFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TestEnvironmentCategory'

    name = factory.Sequence(lambda n: 'Environment Category %d' % n)
    product = factory.SubFactory(ProductFactory)


class TestEnvironmentElementFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TestEnvironmentElement'

    name = factory.Sequence(lambda n: 'Environment Element %d' % n)
    env_category = factory.SubFactory(TestEnvironmentCategoryFactory)


class TestEnvironmentPropertyFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TestEnvironmentProperty'

    name = factory.Sequence(lambda n: 'Environment Property %d' % n)
    element = factory.SubFactory(TestEnvironmentElementFactory)


class TestEnvironmentMapFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TestEnvironmentMap'

    environment = factory.SubFactory(TestEnvironmentFactory)
    property = factory.SubFactory(TestEnvironmentPropertyFactory)
    element = factory.SubFactory(TestEnvironmentElementFactory)


class TestTagFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TestTag'

    name = factory.Sequence(lambda n: 'Tag %d' % n)


class TestAttachmentFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TestAttachment'

    file_name = factory.LazyFunction(lambda: '%s.png' % str(datetime.now()))
    submitter = factory.SubFactory(UserFactory)
    create_date = factory.LazyFunction(datetime.now)
    description = factory.Sequence(lambda n: 'Attachment Image %d' % n)


class TestAttachmentDataFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TestAttachmentData'

    contents = factory.Sequence(lambda n: 'content %d' % n)
    attachment = factory.SubFactory(TestAttachmentFactory)


class TCMSEnvGroupFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TCMSEnvGroup'

    name = factory.Sequence(lambda n: 'Env group %d' % n)
    manager = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)

    @factory.post_generation
    def property(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for property in extracted:
                TCMSEnvGroupPropertyMapFactory(group=self, property=property)


class TCMSEnvPropertyFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TCMSEnvProperty'

    name = factory.Sequence(lambda n: 'Env property %d' % n)


class TCMSEnvGroupPropertyMapFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TCMSEnvGroupPropertyMap'

    group = factory.SubFactory(TCMSEnvGroupFactory)
    property = factory.SubFactory(TCMSEnvPropertyFactory)


class TCMSEnvValueFactory(DjangoModelFactory):

    class Meta:
        model = 'management.TCMSEnvValue'

    value = factory.Sequence(lambda n: 'Env value %d' % n)
    property = factory.SubFactory(TCMSEnvPropertyFactory)


# ### Factories for app testplans ###


class TestPlanTypeFactory(DjangoModelFactory):

    class Meta:
        model = 'testplans.TestPlanType'

    name = factory.Sequence(lambda n: 'Plan type %d' % n)


class TestPlanFactory(DjangoModelFactory):

    class Meta:
        model = 'testplans.TestPlan'

    name = factory.Sequence(lambda n: 'Plan name %d' % n)
    create_date = factory.LazyFunction(datetime.now)
    product_version = factory.SubFactory(VersionFactory)
    owner = factory.SubFactory(UserFactory)
    author = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
    type = factory.SubFactory(TestPlanTypeFactory)
    # FIXME: How to create field for field parent

    @factory.post_generation
    def attachment(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for attachment in extracted:
                TestPlanAttachmentFactory(plan=self, attachment=attachment)

    @factory.post_generation
    def component(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for component in extracted:
                TestPlanComponentFactory(plan=self, component=component)

    @factory.post_generation
    def env_group(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for group in extracted:
                TCMSEnvPlanMapFactory(plan=self, group=group)

    @factory.post_generation
    def tag(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                TestPlanTagFactory(plan=self, tag=tag)


class TestPlanAttachmentFactory(DjangoModelFactory):

    class Meta:
        model = 'testplans.TestPlanAttachment'

    plan = factory.SubFactory(TestPlanFactory)
    attachment = factory.SubFactory(TestAttachmentFactory)


class TestPlanTagFactory(DjangoModelFactory):

    class Meta:
        model = 'testplans.TestPlanTag'

    plan = factory.SubFactory(TestPlanFactory)
    tag = factory.SubFactory(TestTagFactory)


class TestPlanComponentFactory(DjangoModelFactory):

    class Meta:
        model = 'testplans.TestPlanComponent'

    plan = factory.SubFactory(TestPlanFactory)
    component = factory.SubFactory(ComponentFactory)


class TCMSEnvPlanMapFactory(DjangoModelFactory):

    class Meta:
        model = 'testplans.TCMSEnvPlanMap'

    plan = factory.SubFactory(TestPlanFactory)
    group = factory.SubFactory(TCMSEnvGroupFactory)


class TestPlanTextFactory(DjangoModelFactory):

    class Meta:
        model = 'testplans.TestPlanText'

    plan = factory.SubFactory(TestPlanFactory)
    plan_text_version = 1
    author = factory.SubFactory(UserFactory)
    create_date = factory.LazyFunction(datetime.now)
    plan_text = factory.Sequence(lambda n: 'Plan text %d' % n)
    checksum = factory.LazyAttribute(lambda obj: md5_hash(obj.plan_text))


class TestPlanEmailSettingsFactory(DjangoModelFactory):

    class Meta:
        model = 'testplans.TestPlanEmailSettings'

    plan = factory.SubFactory(TestPlanFactory)


# ### Factories for app testcases ###


class TestCaseCategoryFactory(DjangoModelFactory):

    class Meta:
        model = 'testcases.TestCaseCategory'

    name = factory.Sequence(lambda n: 'category %d' % n)
    product = factory.SubFactory(ProductFactory)
    description = ''


class TestCaseFactory(DjangoModelFactory):

    class Meta:
        model = 'testcases.TestCase'

    summary = factory.Sequence(lambda n: 'Test case summary %d' % n)
    case_status = factory.LazyFunction(lambda: TestCaseStatus.objects.all()[0:1][0])
    priority = factory.LazyFunction(lambda: Priority.objects.all()[0:1][0])
    category = factory.SubFactory(TestCaseCategoryFactory)
    author = factory.SubFactory(UserFactory)
    default_tester = factory.SubFactory(UserFactory)
    reviewer = factory.SubFactory(UserFactory)

    @factory.post_generation
    def attachment(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for attachment in extracted:
                TestCaseAttachmentFactory(case=self, attachment=attachment)

    @factory.post_generation
    def plan(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for plan in extracted:
                TestCasePlanFactory(case=self, plan=plan)

    @factory.post_generation
    def component(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for component in extracted:
                TestCaseComponentFactory(case=self, component=component)

    @factory.post_generation
    def tag(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                TestCaseTagFactory(case=self, tag=tag)


class TestCasePlanFactory(DjangoModelFactory):

    class Meta:
        model = 'testcases.TestCasePlan'

    plan = factory.SubFactory(TestPlanFactory)
    case = factory.SubFactory(TestCaseFactory)
    sortkey = factory.Sequence(lambda n: n)


class TestCaseAttachmentFactory(DjangoModelFactory):

    class Meta:
        model = 'testcases.TestCaseAttachment'

    attachment = factory.SubFactory(TestAttachmentFactory)
    case = factory.SubFactory(TestCaseFactory)
    case_run = factory.SubFactory('tests.TestCaseRunFactory')


class TestCaseComponentFactory(DjangoModelFactory):

    class Meta:
        model = 'testcases.TestCaseComponent'

    case = factory.SubFactory(TestCaseFactory)
    component = factory.SubFactory(ComponentFactory)


class TestCaseTagFactory(DjangoModelFactory):

    class Meta:
        model = 'testcases.TestCaseTag'

    case = factory.SubFactory(TestCaseFactory)
    tag = factory.SubFactory(TestTagFactory)
    user = 0


class TestCaseTextFactory(DjangoModelFactory):

    class Meta:
        model = 'testcases.TestCaseText'

    case = factory.SubFactory(TestCaseFactory)
    case_text_version = 1
    author = factory.SubFactory(UserFactory)
    action = 'action'
    effect = 'effect'
    setup = 'setup'
    breakdown = 'breakdown'
    action_checksum = factory.LazyAttribute(lambda obj: md5_hash(obj.action))
    effect_checksum = factory.LazyAttribute(lambda obj: md5_hash(obj.effect))
    setup_checksum = factory.LazyAttribute(lambda obj: md5_hash(obj.setup))
    breakdown_checksum = factory.LazyAttribute(lambda obj: md5_hash(obj.breakdown))


class TestCaseBugFactory(DjangoModelFactory):

    class Meta:
        model = 'testcases.TestCaseBug'

    bug_id = '12345678'
    summary = factory.LazyAttribute(lambda obj: 'Summary of bug %s' % obj.bug_id)
    description = ''
    bug_system = factory.LazyFunction(lambda: TestCaseBugSystem.objects.all()[0:1][0])
    case_run = factory.SubFactory('tests.TestCaseRunFactory')
    case = factory.SubFactory(TestCaseFactory)


class ContactFactory(DjangoModelFactory):

    class Meta:
        model = 'testcases.Contact'

    name = factory.Sequence(lambda n: 'contact_%d' % n)
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.name.replace(' ', '_'))


class TestCaseEmailSettingsFactory(DjangoModelFactory):

    class Meta:
        model = 'testcases.TestCaseEmailSettings'

    case = factory.SubFactory(TestCaseFactory)


# ### Factories for apps testruns ###


class TestRunFactory(DjangoModelFactory):

    class Meta:
        model = 'testruns.TestRun'

    summary = factory.Sequence(lambda n: 'Test run summary %d' % n)
    product_version = factory.SubFactory(VersionFactory)
    plan_text_version = 1
    stop_date = None
    errata_id = None
    notes = ''
    plan = factory.SubFactory(TestPlanFactory)
    # FIXME: field name build conflicts with method Factory.build
    build = factory.SubFactory(TestBuildFactory)
    manager = factory.SubFactory(UserFactory)
    default_tester = factory.SubFactory(UserFactory)

    @factory.post_generation
    def env_group(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for value in extracted:
                TCMSEnvRunValueMapFactory(run=self, value=value)

    @factory.post_generation
    def tag(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                TestRunTagFactory(run=self, tag=tag)

    @factory.post_generation
    def cc(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for user in extracted:
                TestRunCCFactory(run=self, user=user)


class TestCaseRunFactory(DjangoModelFactory):

    class Meta:
        model = 'testruns.TestCaseRun'

    assignee = factory.SubFactory(UserFactory)
    tested_by = factory.SubFactory(UserFactory)
    case_text_version = 1
    running_date = None
    close_date = None
    notes = ''
    sortkey = factory.Sequence(lambda n: n)
    run = factory.SubFactory(TestRunFactory)
    case = factory.SubFactory(TestCaseFactory)
    case_run_status = factory.LazyFunction(lambda: TestCaseRunStatus.objects.all()[0:1][0])
    build = factory.SubFactory(TestBuildFactory)


class TestRunTagFactory(DjangoModelFactory):

    class Meta:
        model = 'testruns.TestRunTag'

    tag = factory.SubFactory(TestTagFactory)
    run = factory.SubFactory(TestRunFactory)


class TestRunCCFactory(DjangoModelFactory):

    class Meta:
        model = 'testruns.TestRunCC'

    run = factory.SubFactory(TestRunFactory)
    user = factory.SubFactory(UserFactory)


class TCMSEnvRunValueMapFactory(DjangoModelFactory):

    class Meta:
        model = 'testruns.TCMSEnvRunValueMap'

    run = factory.SubFactory(TestRunFactory)
    value = factory.SubFactory(TCMSEnvValueFactory)


# ### Factories for app profiles ###


class ProfilesFactory(DjangoModelFactory):

    class Meta:
        model = 'profiles.Profiles'

    login_name = factory.Sequence(lambda n: 'Profile login name %d' % n)
    cryptpassword = 'crypted password'
    realname = factory.LazyAttribute(lambda obj: "%s's realname" % obj.login_name)
    disabledtext = ''
    mybugslink = 1


class GroupsFactory(DjangoModelFactory):

    class Meta:
        model = 'profiles.Groups'

    name = factory.Sequence(lambda n: 'Group name %d' % n)
    description = ''
    isbuggroup = 0
    userregexp = ''
    isactive = 0


class UserGroupMapFactory(DjangoModelFactory):

    class Meta:
        model = 'profiles.UserGroupMap'

    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupsFactory)


class UserProfileFactory(DjangoModelFactory):

    class Meta:
        model = 'profiles.UserProfile'

    user = factory.SubFactory(UserFactory)


class BookmarkCategoryFactory(DjangoModelFactory):

    class Meta:
        model = 'profiles.BookmarkCategory'

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: 'Bookmark category %d' % n)


class BookmarkFactory(DjangoModelFactory):

    class Meta:
        model = 'profiles.Bookmark'

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(BookmarkCategoryFactory)
    name = factory.Sequence(lambda n: 'Bookmark %d' % n)
    description = ''
    url = 'http://localhost/plan/1'
