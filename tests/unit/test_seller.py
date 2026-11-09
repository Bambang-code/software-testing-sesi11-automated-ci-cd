import pytest

from zenta_auth.seller import (
    ApplicationStatus as S,
    ClothingSellerApplication,
    FoodSellerApplication,
    InvalidTransitionError,
    SellerApplication,
)


# Oracle eksplisit dari tabel transisi, bukan dihitung dari implementasi.
TRANSITIONS = [
    (S.DRAFT, "submit", S.PENDING),
    (S.DRAFT, "approve", None),
    (S.DRAFT, "reject", None),
    (S.DRAFT, "withdraw", None),
    (S.PENDING, "submit", None),
    (S.PENDING, "approve", S.APPROVED),
    (S.PENDING, "reject", S.REJECTED),
    (S.PENDING, "withdraw", S.DRAFT),
    (S.APPROVED, "submit", None),
    (S.APPROVED, "approve", None),
    (S.APPROVED, "reject", None),
    (S.APPROVED, "withdraw", None),
    (S.REJECTED, "submit", None),
    (S.REJECTED, "approve", None),
    (S.REJECTED, "reject", None),
    (S.REJECTED, "withdraw", None),
]
IMPLEMENTATIONS = [SellerApplication, FoodSellerApplication, ClothingSellerApplication]


@pytest.fixture(params=IMPLEMENTATIONS, ids=["base", "food", "clothing"])
def application_class(request):
    return request.param


def make_application(application_class, state):
    """Bangun state hanya lewat method publik; setiap test memakai objek baru."""
    application = application_class("Kedai Demo")
    if state != S.DRAFT:
        application.submit()
    if state == S.APPROVED:
        application.approve()
    if state == S.REJECTED:
        application.reject("Dokumen belum lengkap")
    return application


def snapshot(application):
    return application.status, application.shop_name, application.rejection_reason


@pytest.mark.parametrize(
    "initial,event,expected", TRANSITIONS,
    ids=[f"{initial.value}-{event}" for initial, event, _ in TRANSITIONS],
)
def test_entire_transition_contract(application_class, initial, event, expected):
    application = make_application(application_class, initial)
    before = snapshot(application)
    action = getattr(application, event)
    args = ("  Dokumen tidak sesuai  ",) if event == "reject" else ()

    if expected is None:
        with pytest.raises(InvalidTransitionError):
            action(*args)
        assert snapshot(application) == before  # kegagalan tidak merusak state
    else:
        assert action(*args) is None
        assert application.status == expected
        assert application.shop_name == "Kedai Demo"
        if expected == S.REJECTED:
            assert application.rejection_reason == "Dokumen tidak sesuai"
        else:
            assert application.rejection_reason is None


def test_initial_state_and_normalized_name(application_class):
    application = application_class("  Toko Individu  ")
    assert snapshot(application) == (S.DRAFT, "Toko Individu", None)


@pytest.mark.parametrize("name", ["", "   ", "\n\t"])
def test_blank_shop_name_is_rejected(application_class, name):
    with pytest.raises(ValueError, match="^SHOP_NAME_REQUIRED$"):
        application_class(name)


@pytest.mark.parametrize("reason", ["", "   ", "\n\t"])
def test_blank_rejection_reason_leaves_application_pending(application_class, reason):
    application = make_application(application_class, S.PENDING)
    before = snapshot(application)
    with pytest.raises(ValueError, match="^REJECTION_REASON_REQUIRED$"):
        application.reject(reason)
    assert snapshot(application) == before


def test_withdraw_resubmit_then_approve_sequence(application_class):
    application = application_class("Toko Ulang")
    application.submit()
    application.withdraw()
    application.submit()
    application.approve()
    assert snapshot(application) == (S.APPROVED, "Toko Ulang", None)


def test_two_instances_do_not_share_state(application_class):
    first = application_class("Toko A")
    second = application_class("Toko B")
    first.submit()
    assert first.status == S.PENDING
    assert second.status == S.DRAFT


def test_status_cannot_be_assigned_via_public_property(application_class):
    application = application_class("Toko Readonly")
    with pytest.raises(AttributeError):
        application.status = S.APPROVED
    assert application.status == S.DRAFT


@pytest.mark.parametrize(
    "implementation,expected_category",
    [(SellerApplication, "GENERAL"), (FoodSellerApplication, "FOOD"),
     (ClothingSellerApplication, "CLOTHING")],
)
def test_category_override_and_base_contract(implementation, expected_category):
    application = implementation("Toko Kategori")
    assert isinstance(application, SellerApplication)
    assert application.category() == expected_category
    assert application.category().strip()


def test_polymorphic_collection_uses_the_same_interface():
    applications: list[SellerApplication] = [
        FoodSellerApplication("Dapur Demo"), ClothingSellerApplication("Sandang Demo"),
    ]
    assert [application.category() for application in applications] == ["FOOD", "CLOTHING"]
    for application in applications:
        application.submit()
        application.approve()
    assert [application.status for application in applications] == [S.APPROVED, S.APPROVED]
