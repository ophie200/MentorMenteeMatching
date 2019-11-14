from .Mozillian import Mozillian
from .util import safe_cast
from datetime import  datetime
from sortedcontainers import SortedDict
from operator import neg

class Learner(Mozillian):

  def __init__(self, row):
    super().__init__(row)
    self.submitted_dt = row['Timestamp']
    self.time_availability_to_set(row['Time Availability'])
    self.interests_to_set(row['Interested in improving'])
    # if missing change_track value, set to unbias value of 3
    self.change_track = safe_cast(row['Interest in changing career track'], int, 3)
    assert self.change_track in [1,2,3,4,5], self.get_id() + " has invalid change_track value " + str(self.change_track)
    # if missing outside_org value, set to unbias value of 2
    self.outside_org = safe_cast(row['Interest in mentoring or learning from someone outside your own organization?'], int, 2)
    assert self.outside_org in [1,2,3], self.get_id() + " has invalid outside_org value " + str(self.outside_org)
    self.requests = row['Any particular requests?']
    self.identify_as = row['Do you identify yourself as']
    self.welcome_email_dt = row['Sent Wecome Email (date)']
    self.notify_manager_dt = row['Sent Manager Approval Email (date)']
    self.manager_approved_dt = row['Manager Approved (date)']
    
    #self.preferences = SortedDict(neg) #, enumerate('abc', start=1))
    #self.mentor_score = {}
    

  def time_availability_to_set(self, availability):
    """ Set times person is available in set form """
    self.availability_set = set([x.strip() for x in availability.split(',')])
    #print(self.availability_set)
        
        
  def interests_to_set(self, interests):
    """ Set person's interest(s) in set form """
    self.interests_set = set([x.strip() for x in interests.split(',')])
    #print(self.interests_set)
        
        
  def get_submitted_dt(self) -> datetime:
    return self.submitted_dt
        
        
  def get_interests(self) -> set:
    return self.interests_set
        
        
  def get_times_available(self) -> set:
    return self.availability_set


  def get_outside_org_score(self, mentor) -> int:
    # outside org 1=prefer, 3=rather not
    assert mentor.org is not None, "Mentor " + mentor.get_id() + " has invalid org value " + mentor.track
    if self.outside_org==1:
      if self.org == mentor.org:
        return 1
      else:
        return 3
    elif self.outside_org==2:
      if self.org == mentor.org:
        return 2
      else:
        return 2
    elif self.outside_org==3:
      if self.org == mentor.org:
        return 3
      else:
        return 1


  def get_change_track_score(self, mentor) -> int:
    # change career track 1=not interested, 5=very interested => give pref to mentors outside 
    assert mentor.track is not None, "Mentor " + mentor.get_id() + " has invalid track value " + mentor.track
    if self.change_track==1:
      if self.track != mentor.track:
        return 1
      else:
        return 5
    if self.change_track==2:
      if self.track != mentor.track:
        return 2
      else:
        return 4
    if self.change_track==3:
      if self.track != mentor.track:
        return 3
      else:
        return 3
    if self.change_track==4:
      if self.track != mentor.track:
        return 4
      else:
        return 1
    if self.change_track==5:
      if self.track != mentor.track:
        return 5
      else:
        return 1


  def calc_score(self, mentor, is_requested):
    # get count of overlapping times
    available_times = len(self.availability_set.intersection(mentor.get_times_available()))

    # If constraints are satisfied, calculate preference rankings for learners based on feature vector
    score = 0
      
    # add bias for requested mentor
    if is_requested:
      score = score + 50
        
    if available_times > 0:
      # match expertise to interest, max score of 7
      # need to account for "Other:" somehow
      score = score + len(self.interests_set.intersection(mentor.get_expertise()))

      score = score + self.get_outside_org_score(mentor)
      score = score + self.get_change_track_score(mentor)
    return score
    

  def set_preferences(self, mentors:dict, requested_mentor=""):
    self.preferences = SortedDict(neg) #, enumerate('abc', start=1))
    self.mentor_score = {}
    
    for mentor_id, mentor in mentors.items():
      # Filter on constraints    	
      # cannot match to themselves
      if self.get_id() == mentor_id:
        continue
      # mentor-learner should not be in the same management reporting chain - will need ppl dataset info
      # for now just check that learner's manager = mentor or mentor's manager = learner
      if self.get_manager_email() == mentor_id or mentor.get_manager_email() ==self.get_id():
        continue

      # unless manager says "no", manager approved column has no impact
   
      # get count of overlapping times
      available_times = len(self.availability_set.intersection(mentor.get_times_available()))

      # If constraints are satisfied, calculate preference rankings for mentors based on feature vector
      score = 0

      # add bias for requested mentor
      if mentor_id==requested_mentor:
        score = score + 50

      if available_times > 0:

        # attribute, rank, weight
        # score will be learner's sum of weighted attributes

        # match interests to expertise, max score of 7
        # need to account for "Other:" somehow
        score = score + len(self.interests_set.intersection(mentor.get_expertise()))
        #print("interests intersection score:" + str(score))
          
        score = score + self.get_outside_org_score(mentor)
        score = score + self.get_change_track_score(mentor)

        # so far learner ranks range is [2,18]

        # be careful matching those in relationship/married/dating/familial - How??

        # option to constrain mentor org level > learner org level? do levels translate across M/P?

        # if score is the same, order by date_submitted? no i think this is used in the apposite & global draw 
        #print(mentor.get_id() + ": " + str(score))
        
        if score > 0:
          if self.preferences.__contains__(score):
            self.preferences[score].append(mentor)
          else:
            self.preferences[score] = [mentor]
          #data_dict[regNumber].append(details) if self.preferences.__contains__(score) else self.preferences.update({score : [mentor]})
          self.mentor_score[mentor_id] = score

  def get_preferences(self) -> SortedDict:
    return self.preferences
    
  def get_ranked_mentors(self) -> list:
    ranked_mentors = []
    # add weights to those scores that are the same?
    for value in self.preferences.values():
      ranked_mentors.extend([x.get_id() for x in value])
    return ranked_mentors
  
  def get_mentor_score(self) -> dict:
    return self.mentor_score
  
  
  def get_mentor_rank(self, mentor, is_requested) -> int:
    #scores = [score for subscribed_learner_id, score in self.learner_score.items() if subscribed_learner_id == learner.get_id()]
    return self.calc_score(mentor, is_requested)
    
  #def get_mentor_rank(self, mentor) -> int:
  #  scores = [score for mentor_id, score in self.mentor_score.items() if mentor_id == mentor.get_id()]
  #  if len(scores) == 1:
  #    return scores[0]
  #  else:
  #    print("Error in get_learner_rank " + str(len(scores)) + "scores found.")
  #    #return 0
