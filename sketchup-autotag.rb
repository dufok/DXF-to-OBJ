model = Sketchup.active_model
layers = model.layers
entities = model.active_entities

model.start_operation('Auto-tag by component name', true)

entities.grep(Sketchup::ComponentInstance).each do |instance|
  tag_name = instance.definition.name

  # create tag if it doesn't exist yet
  tag = layers[tag_name] || layers.add(tag_name)

  # assign tag to this instance
  instance.layer = tag

  puts "Tagged: #{tag_name}"
end

model.commit_operation
puts "Done! All components tagged."
