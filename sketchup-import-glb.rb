import_dir = "./glb_export"

files = Dir.glob("#{import_dir}/*.glb")
puts "Found #{files.count} GLB files..."

files.each_with_index do |filepath, i|
  puts "[#{i+1}/#{files.count}] Importing #{File.basename(filepath)}..."
  Sketchup.active_model.import(filepath)
end

puts "Done! All GLB files imported."
