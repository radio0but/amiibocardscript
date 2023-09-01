import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango
import xml.etree.ElementTree as ET



class Instructions(Gtk.Box):
    def __init__(self):
        super().__init__(spacing=10)

        # Create a ScrolledWindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        
        # Create a TextView and set its properties
        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        
        # Text buffer and tag table
        tag_table = Gtk.TextTagTable()
        
        # Create tags for various styles and add to the tag table
        self.create_and_add_tag(tag_table, "bold", weight=Pango.Weight.BOLD)
  # Using string 'bold' directly
        self.create_and_add_tag(tag_table, "italic", style=Pango.Style.ITALIC)  # Using Pango for italic
        self.create_and_add_tag(tag_table, "underline", underline=Pango.Underline.SINGLE)  # Using Pango for underline
        self.create_and_add_tag(tag_table, "red_foreground", foreground="red")
        
        text_buffer = Gtk.TextBuffer.new(tag_table)
        textview.set_buffer(text_buffer)
        
        # Parse the markup and apply the tags to the buffer
        self.parse_markup_and_apply_tags(text_buffer)
        
        # Add the TextView to the ScrolledWindow
        scrolled_window.add(textview)

        # Pack the ScrolledWindow into the box
        self.pack_start(scrolled_window, True, True, 0)

    def create_and_add_tag(self, tag_table, name, **properties):
        tag = Gtk.TextTag.new(name)
        for prop, value in properties.items():
            tag.set_property(prop, value)
        tag_table.add(tag)
        
    def parse_markup_and_apply_tags(self, text_buffer):
        markup = """
<markup>

<br><br><u><b>Initiate the Amiibo Download Process:</b></u></br></br>

<br><br><i>Click on the "Download" button to launch the Amiibo downloader application.</i></br></br>

<br><br><b>Within the Amiibo "Step 1: Cards Downloader" Tab:</b></br></br>

<br><br><u><b>Select Images:</b></u></br></br>

<br><i>Choose 9 images by clicking on them individually.</i></br>
<br><i>Confirm your selections by clicking the "Download" button.</i></br>
<br><i>Utilize the search bar to filter images by Series or name for quicker navigation.</i></br>
<br><br><span foreground="red"><i>Note: The application may behave unpredictably due to the large number of amiibo available. Please leave time for all the Amiibo to load before changing filters. </i></span></br></br>

<br><br><u><b>Complete the Download:</b></u></br></br>

<br><i>Click "Download" and wait until the button returns to its normal state, indicating the download is complete.</i></br>
<br><br><i>Exit the downloader app by clicking the "x" in the top right corner.</i></br></br>



<br><br><u><b>Prepare the Print:</b></u></br></br>

<br><br><i>Click the "Step 2: PDF Generator" button to open the Amiibo print preparation Tab.</i></br></br>

<br><br><b>Within the "Step 2: PDF Generator" Tab:</b></br></br>

<br><br><u><b>Configure the Print Settings:</b></u></br></br>

<br><i>Select the desired orientation.</i></br>
<br><i>Preview the layout.</i></br>
<br><br><i>Generate the PDF, allowing the images to be stretched to fit the cards.</i></br></br>

<br><br><u><b>Finalize the Print Prep:</b></u></br></br>

<br><i>Upon successful PDF creation, a message will appear indicating that the process is complete.</i></br>


<br><br><b>Select the "Step 3 : Print" Tab</b></br></br>

<br><br><u><b>Print the Cards:</b></u></br></br>

<br><br><i>Click on the "Print" button, and the cards will be printed using your default printer.</i></br></br>

<br><br><b>By following these steps, you should be able to download, prepare, and print your Amiibo cards seamlessly.</b></br></br>

<br><br><b>Terms &amp; Conditions</b></br>
</br>
<br><br>By using the Amiibo Cards Generator Suite (hereinafter referred to as the "App"), you hereby accept the following terms and conditions:</br>
</br>
<br><br><i>The App, Amiibo Cards Generator Suite, has no affiliation with Nintendo, amiiboAPI, or any other companies that own the rights to them.</i></br>
</br>
<br><br>Reports or information collected by Nintendo, amiiboAPI, or the respective companies that own the rights are not our responsibility.</br>
</br>
<br><br><u>The user agrees that the use of this App is entirely at the user’s own risk.</u></br>
</br>
<br><br>You will require your end users to comply with (and not knowingly enable them to violate) applicable law, regulation, and these Terms.</br>
</br>
<br><br><span foreground="red">You will comply with all applicable laws, regulations, and third-party rights (including, without limitation, laws regarding the import or export of data or software, privacy, and local laws). You will not use the App to encourage or promote illegal activity or violation of third-party rights.</span></br>
</br>
These Terms and Conditions are subject to change without notice, from time to time, in our sole discretion.


</markup>
"""

        # Parse the XML content
        root = ET.fromstring(markup)
        for child in root:
            self.insert_with_tags(text_buffer, child)

    def insert_with_tags(self, buffer, node):
        # Create a mark at the current end of the buffer.
        start_mark = buffer.create_mark(None, buffer.get_end_iter(), left_gravity=True)

        if node.text:
            buffer.insert(buffer.get_end_iter(), node.text)

        for child in node:
            self.insert_with_tags(buffer, child)
            if child.tail:
                buffer.insert(buffer.get_end_iter(), child.tail)

        # Get the start iter from the mark.
        start_iter = buffer.get_iter_at_mark(start_mark)
        end_iter = buffer.get_end_iter()

        if node.tag == "b":
            buffer.apply_tag_by_name("bold", start_iter, end_iter)
        elif node.tag == "i":
            buffer.apply_tag_by_name("italic", start_iter, end_iter)
        elif node.tag == "u":
            buffer.apply_tag_by_name("underline", start_iter, end_iter)
        elif node.tag == "span":
            if 'foreground' in node.attrib and node.attrib['foreground'] == 'red':
                buffer.apply_tag_by_name("red_foreground", start_iter, end_iter)
        elif node.tag == "br":  # Handling <br> tag to insert a new line
            buffer.insert(buffer.get_end_iter(), "\n")

        # Delete the mark after using it.
        buffer.delete_mark(start_mark)