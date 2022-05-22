require 'kindle_highlights'

# puts book.author

puts "hello world"

kindle = KindleHighlights::Client.new(email_address: "maxmonty@pm.me", password: "Eqk5BHRg2PwTPZ")

# begin
#   puts kindle.books.sample
# rescue Exception => e
#   puts e
# end

begin
  puts kindle.books
rescue Exception => e
  puts e
end

return kindle
