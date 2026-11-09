"""State machine lokal pengajuan seller untuk latihan OO testing.

DRAFT dan withdraw adalah penyederhanaan khusus tugas individu, bukan klaim
fitur/kontrak baru pada aplikasi kelompok. Tidak ada role/DB riil yang diubah.
"""

from enum import Enum


class ApplicationStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class InvalidTransitionError(RuntimeError):
    """Event tidak dapat dijalankan dari state saat ini."""


class SellerApplication:
    """Status diamati melalui property publik; keputusan akhir bersifat terminal."""

    def __init__(self, shop_name: str):
        normalized_name = shop_name.strip()
        if not normalized_name:
            raise ValueError("SHOP_NAME_REQUIRED")
        self._shop_name = normalized_name
        self._status = ApplicationStatus.DRAFT
        self._rejection_reason: str | None = None

    @property
    def shop_name(self) -> str:
        return self._shop_name

    @property
    def status(self) -> ApplicationStatus:
        return self._status

    @property
    def rejection_reason(self) -> str | None:
        return self._rejection_reason

    def category(self) -> str:
        """Kontrak polimorfik: nama kategori non-kosong untuk ringkasan aplikasi."""
        return "GENERAL"

    def submit(self) -> None:
        if self.status != ApplicationStatus.DRAFT:
            raise InvalidTransitionError("SUBMIT_REQUIRES_DRAFT")
        self._status = ApplicationStatus.PENDING

    def approve(self) -> None:
        if self.status != ApplicationStatus.PENDING:
            raise InvalidTransitionError("APPROVE_REQUIRES_PENDING")
        self._status = ApplicationStatus.APPROVED

    def reject(self, reason: str) -> None:
        if self.status != ApplicationStatus.PENDING:
            raise InvalidTransitionError("REJECT_REQUIRES_PENDING")
        normalized_reason = reason.strip()
        if not normalized_reason:
            raise ValueError("REJECTION_REASON_REQUIRED")
        self._rejection_reason = normalized_reason
        self._status = ApplicationStatus.REJECTED

    def withdraw(self) -> None:
        if self.status != ApplicationStatus.PENDING:
            raise InvalidTransitionError("WITHDRAW_REQUIRES_PENDING")
        self._status = ApplicationStatus.DRAFT


class FoodSellerApplication(SellerApplication):
    """Mewarisi seluruh aturan transisi, mengkhususkan label kategori."""

    def category(self) -> str:
        return "FOOD"


class ClothingSellerApplication(SellerApplication):
    """Mewarisi seluruh aturan transisi, mengkhususkan label kategori."""

    def category(self) -> str:
        return "CLOTHING"
