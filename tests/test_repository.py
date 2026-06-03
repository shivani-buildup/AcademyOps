import pytest
from src.models import Lead, LeadStage
from src.exceptions import DuplicatePhoneError, LeadNotFound, InvalidStageError

def test_create_and_get_lead(in_memory_repo):
    lead = Lead(name="Test User", phone="111-2222", source="Facebook")
    created = in_memory_repo.create(lead)
    
    assert created.id is not None
    assert created.stage == LeadStage.NEW
    
    fetched = in_memory_repo.get(created.id)
    assert fetched.name == "Test User"
    assert fetched.phone == "111-2222"

def test_create_duplicate_phone(in_memory_repo):
    lead1 = Lead(name="User One", phone="555-0000")
    in_memory_repo.create(lead1)
    
    lead2 = Lead(name="User Two", phone="555-0000")
    with pytest.raises(DuplicatePhoneError):
        in_memory_repo.create(lead2)

def test_get_nonexistent_lead(in_memory_repo):
    with pytest.raises(LeadNotFound):
        in_memory_repo.get(999)

def test_list_leads_with_filters(in_memory_repo):
    in_memory_repo.create(Lead(name="User 1", phone="111", source="Facebook"))
    in_memory_repo.create(Lead(name="User 2", phone="222", source="Website"))
    
    lead3 = in_memory_repo.create(Lead(name="User 3", phone="333", source="Facebook"))
    in_memory_repo.update_stage(lead3.id, LeadStage.CONTACTED)
    
    all_leads = in_memory_repo.list()
    assert len(all_leads) == 3
    
    fb_leads = in_memory_repo.list(source="Facebook")
    assert len(fb_leads) == 2
    
    contacted_fb = in_memory_repo.list(source="Facebook", stage=LeadStage.CONTACTED.value)
    assert len(contacted_fb) == 1
    assert contacted_fb[0].name == "User 3"

def test_update_stage(in_memory_repo):
    lead = in_memory_repo.create(Lead(name="Test", phone="1234"))
    
    updated = in_memory_repo.update_stage(lead.id, "Qualified")
    assert updated.stage == LeadStage.QUALIFIED
    
    fetched = in_memory_repo.get(lead.id)
    assert fetched.stage == LeadStage.QUALIFIED

def test_update_invalid_stage(in_memory_repo):
    lead = in_memory_repo.create(Lead(name="Test", phone="1234"))
    
    with pytest.raises(InvalidStageError):
        in_memory_repo.update_stage(lead.id, "FakeStage")

def test_delete_lead(in_memory_repo):
    lead = in_memory_repo.create(Lead(name="Test", phone="1234"))
    in_memory_repo.delete(lead.id)
    
    with pytest.raises(LeadNotFound):
        in_memory_repo.get(lead.id)

def test_delete_nonexistent_lead(in_memory_repo):
    with pytest.raises(LeadNotFound):
        in_memory_repo.delete(999)
