from Models.home import Home

model = Home()
model.step()
model.visible_stakeholders_to_robot()
print(model.get_location((5, 6)))
print(model.get_location((5, 7)))