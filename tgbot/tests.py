import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils.timezone import now

import tgbot.exceptions as exc
from bazaarapp.processors import (
    LocationConfirmationProcessor,
    LocationKeyInputProcessor,
)
from convoapp.processors import (
    CarTypeInputProcessor,
    DescriptionInputProcessor,
    FeedbackInputProcessor,
    NameInputProcessor,
    SetReadyInputProcessor,
    StartInputProcessor,
    StorePhotoInputProcessor,
    TagInputProcessor,
)
from subscribeapp.models import Subscription
from tgbot.models import BotUser, RepairsType
from tgbot.models import RequestFormingStage as RFS
from tgbot.models import WorkRequestStage


class BotUserTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        user, _ = BotUser.objects.get_or_create(
            name="TestUser",
            first_name="Test",
            last_name="User",
            user_id=11111,
            username="TestUser",
            location="Санкт-Петербург, Россия",
            phone="+77777777777",
            is_banned=False,
            is_staff=False,
            company_name="СТО Тест",
        )

    def setUp(self) -> None:
        self.user: BotUser = BotUser.objects.get(user_id=11111)

    def test_get_fullname(self):
        """test get_fullname property returns a full user name"""

        self.assertEqual(self.user.get_fullname, "Test User")

    def test_str_repr(self):
        """test that the string representation of a user works properly"""

        self.assertEqual(str(self.user)[2:], " TestUser TG: #11111 @TestUser")
        self.user.name = ""
        self.assertEqual(str(self.user)[2:], " Test User TG: #11111 @TestUser")
        self.user.username = ""
        self.assertEqual(str(self.user)[2:], " Test User TG: #11111 @-")

    def test_get_or_create(self):
        """tests that the class objects are correctly retrieved and created"""

        data = dict(
            user_id=22222,
            username="CreatedTestUser",
            first_name="Created",
            last_name="User",
        )
        user2, created = BotUser.get_or_create(data)
        self.assertEqual(str(user2)[2:], " Created User TG: #22222 @CreatedTestUser")
        self.assertTrue(created)
        user3, created = BotUser.get_or_create(data)
        self.assertEqual(str(user3)[2:], " Created User TG: #22222 @CreatedTestUser")
        self.assertEqual(user2, user3)
        self.assertFalse(created)
        user2.is_banned = True
        user2.save()
        with self.assertRaises(exc.UserIsBannedError):
            user, created = BotUser.get_or_create(data)

    def test_ban(self):
        """test user ban function"""
        data = dict(
            user_id=22222,
            username="CreatedTestUser",
            first_name="Created",
            last_name="User",
        )
        user2: BotUser
        user2, created = BotUser.get_or_create(data)
        self.assertFalse(user2.is_banned)
        user2.ban()
        self.assertTrue(user2.is_banned)
        with self.assertRaises(exc.UserIsBannedError):
            user2.ban()

    def test_subscribed_to_service(self):
        """test service subscription check function"""

        self.assertIsNone(self.user.subscribed_to_service(1))
        sub = Subscription.get_or_create(self.user, 1, "RepairsFilter")
        self.assertIsNone(self.user.subscribed_to_service(1))
        sub.activate()
        self.assertLessEqual(
            self.user.subscribed_to_service(1) - (now() + relativedelta(months=1)),
            datetime.timedelta(milliseconds=1),
        )


class RepairsTypeTestCase(TestCase):
    def test_repairs_type_repr(self):
        """test string representation of a repairstype tag"""
        rt: RepairsType = RepairsType.objects.get(pk=1)
        self.assertEqual(str(rt), "#1 Другое")

    def test_get_tag_by_name(self):
        """test getting the repairs type tag by name"""
        rt: RepairsType = RepairsType.get_tag_by_name("Другое")
        self.assertEqual(rt.pk, 1)


class WorkRequestStageTestCase(TestCase):
    """Набор тестов для класса стадий заполнения заявки"""

    def test_get_processor(self):
        """test getting the corresponding processor for the stage"""
        self.maxDiff = None
        processors = [
            stage.get_processor()
            for stage in WorkRequestStage.objects.all().order_by("pk")
        ]
        self.assertEqual(
            processors,
            [
                StartInputProcessor,
                NameInputProcessor,
                TagInputProcessor,
                CarTypeInputProcessor,
                DescriptionInputProcessor,
                StorePhotoInputProcessor,
                LocationKeyInputProcessor,
                LocationConfirmationProcessor,
                SetReadyInputProcessor,
                None,
                FeedbackInputProcessor,
                None,
            ],
        )

    def test_get_by_callback(self):
        """test getting the corresponding stage for callback shortcuts"""
        wrs: WorkRequestStage = WorkRequestStage.objects.get(pk=1)
        self.assertEqual(wrs.get_by_callback("new_request"), RFS.GET_NAME)
        self.assertEqual(wrs.get_by_callback("restart"), RFS.WELCOME)
        self.assertEqual(wrs.get_by_callback("leave_feedback"), RFS.LEAVE_FEEDBACK)


class WorkRequestTestCase(TestCase):
    """Проверка функций класса заявки на работу"""
