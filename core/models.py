# #cloning

# from copy import deepcopy
# from itertools import chain
# from mrvapi.models import Project, Parcel, ProjectPermissions
# import ecalc


# # get the project from the database by ID 
# #call clone method in project class in mrvapi.models
# # new project CREATED in that clone method
# #store in a variable

# def cloneproject(pk,new_owner,new_name):

# 	project = Project.objects.get(id=pk) #Getting project from database by ID
#     #Copies project, stores in variable
# 	new_project = project.clone(new_owner,new_name) #calling clone method in mrvapi.models

# 	#Permissions
# 	#project.mainProjectPermission = ProjectPermissions.objects.get(project = project.id, user=project.owner)
# 	#project.mainProjectPermission.clone(new_project)

#     #Next, parcels, get all the parcels associated with that ID, call clone method with all those objects
#     #pass back new parcel object

#     #project.default_parcel.clone_children(clone, clone.default_parcel)
# 	new_parcel = []
# 	children = list(chain(project.parcel_set.all(), project.projectboundary_set.all()))
# 	for child in children:
# 		new_parcel.append(child.clone(new_project))  # This calls the children clone function with our new clone ID as parent



# 	#Create a new AEQ
# 	if project.aeq:
# 		new_project.aeq = project.aeq.clone(new_project.owner)

#     #Next, plots
# 	#raise Exception("test")
#     #Next, trees

#     #Once everything is copied, "need to start saving and associated IDS"
#     #then assign an ID by the database
#     #return None

# class ProjectClone(Project):

# 	def __init__(self,project,new_owner,new_name=""):

# 		""" Returns a copy of itself, with a new ID and new FK parent, and with all new copied children """
# 		self.project = project #instance variable
# 		clone = deepcopy(self.project) #class variable
# 		clone.id = None
# 		clone.owner = new_owner
# 		if new_name == "":
# 			new_name = self.project.name
# 		clone.name = new_name
# 		#should not save clone until everything is completed, returning a fully copied project
# 		clone.save(clone=True)  # This will create the clone and give it a new ID
# 		clone.reset_secret_code()  # special case 1: we need to generate a unique secret key for the project

# 	def clonePermissions(self):
# 		# Permissions
# 		#self.mainProjectPermission = ProjectPermissions.objects.get(project = self.id, user=self.owner)
# 		self.mainProjectPermission.clone(clone)

# 	def cloneParcel(self):

#     	# special case: we need to clone the default_parcel (done before other parcels to preserve ordering in dropdown menus)
#         # self.default_parcel.clone(clone)
# 		self.default_parcel.clone_children(clone, clone.default_parcel)

#         # Next, we need to iterate through descendant objects and give them our new PK by calling .clone(PK)
#         # Note that parcel_set() excludes the hidden default_parcel, so we are good and aren't doing that one twice
# 		children = list(chain(self.parcel_set.all(), self.projectboundary_set.all()))
# 		for child in children:
# 			child.clone(clone)  # This calls the children clone function with our new clone ID as parent

# 	def cloneAEQ(self):
# 		# Create a new AEQ
# 		if self.aeq:
# 			clone.aeq = self.aeq.clone(clone.owner)

# 	def cloneLandCover(self):

# 		children = list(chain( self.landcover_set.all()))

#    	def clonePracticeSet(self):
# 		children = list(chain( self.practice_set.all()))

#    	def cloneScenario(self):
#         # ECALC relations cloning
#         # Next, we need to iterate through descendant objects and give them our new PK by calling .clone(PK)
# 		delta_dict = dict()  # delta_dict is mutable, and gets the new Object/FK relation ids keyed by old {(obj.__class__.__doc__, old_id): new_id
#         #delta_dict[(self.__doc__, self.id)] = clone.id
# 		children = list(chain( self.scenario_set.filter(reference_scenario=None), self.scenario_set.filter(reference_scenario=True)
#                                 # it is important that you do reference scenarios first, i.e. ref=None (not a proj scen)
#                               ))
# 		for child in children:
# 			child.clone(delta_dict)

#         # finally, save the clone
#         #clone.save()

#         #return clone