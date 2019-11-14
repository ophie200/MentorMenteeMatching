
class Mozillian:
  """ A class to represent a person attributes """

  def __init__(self, row): # email, org_level, org, full_name, manager_email):

    self.email = str(row['Email Address']).lower()
    self.org_level = row['Organizational level (i.e. P3, M2, etc.)']
    self.track = self.org_level[0]
    self.org = row['Organization']
    self.full_name = row['Participant full name']
    self.manager_email = str(row['Manager email']).lower()
    # add something for reporting chains including self

  def get_id(self) -> str:
    """ person's unique identifier """
    return self.email

  def get_org_level(self) -> str:
    return self.org_level
        
  def get_track(self) -> str:
    return self.track

  def get_org(self) -> str:
    return self.org
        
  def get_manager_email(self) -> str:
    return self.manager_email