import random
import sys
import datetime

QUOTES = [
    {"text": "Data is the new oil, but only if you know how to refine it.", "author": "Clive Humby"},
    {"text": "The goal is to turn data into information, and information into insight.", "author": "Carly Fiorina"},
    {"text": "Without big data analytics, companies are blind and deaf, wandering onto the web like deer on a freeway.", "author": "Geoffrey Moore"},
    {"text": "In God we trust, all others must bring data.", "author": "W. Edwards Deming"},
    {"text": "Data that is loved tends to survive.", "author": "Kurt Bollacker"},
    {"text": "Errors using inadequate data are much less than those using no data at all.", "author": "Charles Babbage"},
    {"text": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"},
    {"text": "Programs must be written for people to read, and only incidentally for machines to execute.", "author": "Harold Abelson"},
    {"text": "Always code as if the guy who ends up maintaining your code will be a violent psychopath who knows where you live.", "author": "John Woods"},
    {"text": "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "author": "Martin Fowler"},
    {"text": "First, solve the problem. Then, write the code.", "author": "John Johnson"},
    {"text": "Experience is the name everyone gives to their mistakes.", "author": "Oscar Wilde"},
    {"text": "Knowledge is power.", "author": "Francis Bacon"},
    {"text": "Sometimes it pays to stay in bed on Monday, rather than spending the rest of the week debugging Monday's code.", "author": "Dan Salomon"},
    {"text": "Perfection is achieved not when there is nothing more to add, but rather when there is nothing more to take away.", "author": "Antoine de Saint-Exupery"},
    {"text": "Ruby is rubbish! PHP is phpantastic!", "author": "Nikita Popov"},
    {"text": "Code is like humor. When you have to explain it, it’s bad.", "author": "Cory House"},
    {"text": "Fix the cause, not the symptom.", "author": "Steve Maguire"},
    {"text": "Optimism is an occupational hazard of programming: feedback is the treatment.", "author": "Kent Beck"},
    {"text": "Before software can be reusable it first has to be usable.", "author": "Ralph Johnson"},
    {"text": "Make it work, make it right, make it fast.", "author": "Kent Beck"},
    {"text": "Simplicity is the soul of efficiency.", "author": "Austin Freeman"},
    {"text": "You can't have great software without a great team, and most software teams behave like dysfunctional families.", "author": "Jim McCarthy"},
    {"text": "If at first you don’t succeed; call it version 1.0", "author": "Unknown"},
    {"text": "It’s not a bug. It’s an undocumented feature!", "author": "Anonymous"},
    {"text": "A good programmer is someone who always looks both ways before crossing a one-way street.", "author": "Doug Linder"},
    {"text": "Testing leads to failure, and failure leads to understanding.", "author": "Burt Rutan"},
    {"text": "Software and cathedrals are much the same – first we build them, then we pray.", "author": "Sam Ewing"},
    {"text": "Don't comment bad code - rewrite it.", "author": "Brian Kernighan"},
    {"text": "We have to stop optimizing for programmers and start optimizing for users.", "author": "Jeff Atwood"},
    {"text": "There are two hard things in computer science: cache invalidation, naming things, and off-by-one errors.", "author": "Phil Karlton"},
    {"text": "What one programmer can do in one month, two programmers can do in two months.", "author": "Fred Brooks"},
    {"text": "Programming today is a race between software engineers striving to build bigger and better idiot-proof programs, and the Universe trying to produce bigger and better idiots. So far, the Universe is winning.", "author": "Rick Cook"},
    {"text": "I’m not a great programmer; I’m just a good programmer with great habits.", "author": "Kent Beck"},
    {"text": "Programming is the art of algorithm design and the craft of debugging errant code.", "author": "Ellen Ullman"},
    {"text": "Every great developer you know got there by solving problems they were unqualified to solve until they actually did it.", "author": "Patrick McKenzie"},
    {"text": "Measuring programming progress by lines of code is like measuring airplane building progress by weight.", "author": "Bill Gates"},
    {"text": "Computers are good at following instructions, but not at reading your mind.", "author": "Donald Knuth"},
    {"text": "A language that doesn't affect the way you think about programming is not worth knowing.", "author": "Alan Perlis"},
    {"text": "There is nothing quite so permanent as a quick fix.", "author": "Unknown"},
    {"text": "Software is a great combination between artistry and engineering.", "author": "Bill Gates"},
    {"text": "It is not that we have a short time to live, but that we waste a lot of it.", "author": "Seneca"},
    {"text": "The computer was born to solve problems that did not exist before.", "author": "Bill Gates"},
    {"text": "Let us change our traditional attitude to the construction of programs. Instead of imagining that our main task is to instruct a computer what to do, let us concentrate rather on explaining to human beings what we want a computer to do.", "author": "Donald Knuth"},
    {"text": "Controlling complexity is the essence of computer programming.", "author": "Brian Kernighan"},
    {"text": "Walking on water and developing software from a specification are easy if both are frozen.", "author": "Edward V. Berard"},
    {"text": "The most disastrous thing that you can ever learn is your first programming language.", "author": "Alan Kay"},
    {"text": "I think everybody in this country should learn how to program a computer because it teaches you how to think.", "author": "Steve Jobs"},
    {"text": "Good design adds value faster than it adds cost.", "author": "Thomas C. Gale"},
    {"text": "Python's a drop-in replacement for BASIC in the sense that Optimus Prime is a drop-in replacement for a truck.", "author": "Cory Dodt"}
]

def chunk_text(text, max_length=50):
    words = text.split(" ")
    chunks = []
    current_chunk = ""
    for word in words:
        if len(current_chunk) + len(word) + 1 > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = word + " "
        else:
            current_chunk += word + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def generate_svg():
    # Pick a random quote
    random.seed(datetime.datetime.now().strftime("%Y-%m-%d")) # Seed by date so it stays consistent for the day
    quote = random.choice(QUOTES)
    
    text_chunks = chunk_text(f'"{quote["text"]}"', 50)
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 220" width="800" height="220">
  <style>
    .bg {{ fill: #1E1E1E; }}
    .header-bg {{ fill: #2D2D2D; }}
    .title {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 13px;
      fill: #A0A0A0;
      font-weight: 500;
    }}
    .prompt {{
      font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
      font-size: 13px;
      fill: #00d9ff;
      font-weight: bold;
    }}
    .quote-text {{
      font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
      font-size: 13px;
      fill: #39FF14;
      font-weight: bold;
      opacity: 0;
      animation: type 0.1s forwards;
    }}
    .author-text {{
      font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
      font-size: 12px;
      fill: #ff6b6b;
      font-weight: normal;
      font-style: italic;
      opacity: 0;
      animation: type 0.1s forwards;
    }}
    .cursor {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      fill: #39FF14;
    }}

    @keyframes type {{
      to {{ opacity: 1; }}
    }}
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0; }}
    }}

    .blink-cursor {{
      animation: blink 1s step-end infinite;
    }}
  </style>

  <!-- Terminal Window -->
  <rect width="100%" height="100%" rx="10" class="bg" />

  <!-- MacBook Header -->
  <path d="M 0 10 C 0 4.477 4.477 0 10 0 L 790 0 C 795.523 0 800 4.477 800 10 L 800 30 L 0 30 Z" class="header-bg" />

  <!-- Window Buttons -->
  <circle cx="20" cy="15" r="6" fill="#FF5F56" />
  <circle cx="40" cy="15" r="6" fill="#FFBD2E" />
  <circle cx="60" cy="15" r="6" fill="#27C93F" />

  <!-- Title -->
  <text x="50%" y="20" text-anchor="middle" class="title">quotes@shard-c6:~</text>

  <!-- Prompt -->
  <text x="20" y="60" class="prompt">$ fortune | cowthink</text>
'''
    
    # Add quote lines
    delay = 0.5
    y_pos = 90
    for chunk in text_chunks:
        svg_content += f'  <text x="20" y="{y_pos}" class="quote-text" style="animation-delay: {delay}s">{chunk}</text>\n'
        delay += 0.2
        y_pos += 20
        
    y_pos += 10
    svg_content += f'  <text x="20" y="{y_pos}" class="author-text" style="animation-delay: {delay}s">— {quote["author"]}</text>\n'
    
    # Add final prompt
    delay += 0.5
    y_pos += 40
    svg_content += f'''
  <!-- Prompt 2 -->
  <text x="20" y="{y_pos}" class="prompt" style="opacity: 0; animation: type 0.1s {delay}s forwards">$ <tspan class="blink-cursor">▊</tspan></text>
</svg>
'''

    with open("assets/quotes-terminal.svg", "w") as f:
        f.write(svg_content)
    
    print("Quote SVG generated!")

if __name__ == "__main__":
    generate_svg()
