from bs4 import BeautifulSoup

### prof

html_content = """
<!-- wp:html -->
<div class="chevronProfile color-SDSU"></div>
<div class="header-profile">
    <div class="heading">
        <div class="faculty__image"><img alt="Closeup of Eric Sandquist"
                src="https://astronomy.sdsu.edu/wp-content/uploads/2022/11/eric-sandquist-1024x1024-1-768x768.jpg">
        </div>
        <div class="faculty__heading">
            <h1>Eric Sandquist, Ph.D.</h1>
            <p>Pronouns: he/him/his</p>
            <p class="profileLine"></p>
            <p>Department Chair<br />Professor of Astronomy</p>
            <p><strong>College of Sciences</strong><br>Department of Astronomy<br></p>
            <p>San Diego</p>
        </div>
    </div>
    <div class="profile-content">
        <script src="https://cfcdn.digitalmeasures.com/dm-web-profiles/v2/js/main.js"></script>
        <script src="https://ackerman.sdsu.edu/_resources_insight_child/js/hidethis.js"></script>
        <script>let webid = 1963228; let client = "d8b736df-4e4a-5cc2-964a-4e101a5e608c";</script>
        <div class="faculty-info">
            <dl class="faculty__contact">
                <div id="email" class="hide">
                    <dt class="email">Email</dt>
                    <dd class="faculty__email"><a href="mailto:esandquist@sdsu.edu">esandquist@sdsu.edu</a></dd>
                </div>
                <div id="phone">
                    <dt class="phone">Phone</dt>
                    <dd class="faculty__phone"><a href="tel:619-594-2694">619-594-2694</a></dd>
                </div>
                <div id="hours">
                    <dt class="hours">Office Hours</dt>
                    <dd class="faculty__available">
                        <p>TBA<br /></p>
                    </dd>
                </div>
                <div id="office">
                    <dt class="office">Location</dt>
                    <dd class="faculty__office"><a href="https://map.concept3d.com/?id=801#!m/147095" title="Physics"
                            target="_blank">P</a> 134<br>5500 Campanile Dr<br>San Diego, CA 92182</dd>
                </div>
                <div id="mailcode">
                    <dt class="mail-code">Mail Code</dt>
                    <dd class="faculty__mail"></dd>
                </div>
                <div id="fax">
                    <dt class="fax">Fax</dt>
                    <dd class="faculty__phone"></dd>
                </div>
                <div id="links" undefined>
                    <dt class="links">Links</dt>
                    <dd><a href="https://esandquist.sdsu.edu/" class="faculty__website">Website</a></dd>
                </div>
                <div id="accounts" class="hide">
                    <dt class="accounts">Accounts</dt>
                    <dd>
                        <ul class="sociallinks">
                            <li class="linkedin"><a href="https://linkedin.com/">LinkedIn</a></li>
                        </ul>
                    </dd>
                </div>
            </dl>
        </div>
        <script> contactNull(); </script>
        <div class="content-items">
            <div class="content-expertise">
                <h2>Areas of Expertise</h2>
                <p>Astronomy, astrophysics, stars, star clusters, ages of stars, star collisions, planets consumed by
                    stars</p>
            </div>
            <div class="content-bio">
                <h2>Bio</h2>
                <p>Eric Sandquist works for the Department of Astronomy within the College of Sciences at the San Diego
                    campus as a Department Chair, and Professor.</p>
            </div>
            <div>
                <h2>DETAILS</h2>
                <div class="content-details-2">
                    <div id="education">[su_accordion][su_spoiler title="Education" style="carbon"]
                        <script> window.dmWebProfiles.showProfile({ container: "#dm-web-profile-education", clientId: client, reportId: "7694398b-9377-11ed-b30e-4d17c5023e88", userIdentifier: "WebProfileID", WebProfileID: webid, }); profileNull("7694398b-9377-11ed-b30e-4d17c5023e88", "education");</script>
                        <div id="dm-web-profile-education"></div>[/su_spoiler] [/su_accordion]
                    </div>
                    <div id="publications">[su_accordion] [su_spoiler title="Publications" style="carbon"]
                        <script> window.dmWebProfiles.showProfile({ container: "#dm-web-profile-publications", clientId: client, reportId: "61496646-92a6-11ed-b30e-3bd5b706ea18", userIdentifier: "WebProfileID", WebProfileID: webid, }); profileNull("61496646-92a6-11ed-b30e-3bd5b706ea18", "publications"); </script>
                        <div id="dm-web-profile-publications"></div> [/su_spoiler] [/su_accordion]
                    </div>
                    <div id="presentations">[su_accordion] [su_spoiler title="Presentations" style="carbon"]
                        <script>window.dmWebProfiles.showProfile({ container: "#dm-web-profile-presentations", clientId: client, reportId: "2ebe911c-92b5-11ed-b30e-a7a212c13be5", userIdentifier: "WebProfileID", WebProfileID: webid, }); profileNull("2ebe911c-92b5-11ed-b30e-a7a212c13be5", "presentations");</script>
                        <div id="dm-web-profile-presentations"></div>[/su_spoiler] [/su_accordion]
                    </div>
                    <div id="service">[su_accordion] [su_spoiler title="Service" style="carbon"]
                        <script>window.dmWebProfiles.showProfile({ container: "#dm-web-profile-service", clientId: client, reportId: "37add882-9375-11ed-b30e-71c3f45583b2", userIdentifier: "WebProfileID", WebProfileID: webid, }); profileNull("37add882-9375-11ed-b30e-71c3f45583b2", "service");</script>
                        <div id="dm-web-profile-service"></div>[/su_spoiler] [/su_accordion]
                    </div>
                    <div id="grants">[su_accordion] [su_spoiler title="Grants" style="carbon"]
                        <script> window.dmWebProfiles.showProfile({ container: "#dm-web-profile-grants", clientId: client, reportId: "4d9f8f96-9376-11ed-b30e-43918a716b67", userIdentifier: "WebProfileID", WebProfileID: webid, }); profileNull("4d9f8f96-9376-11ed-b30e-43918a716b67", "grants");</script>
                        <div id="dm-web-profile-grants"></div>[/su_spoiler] [/su_accordion]
                    </div>
                    <div id="awards">[su_accordion] [su_spoiler title="Awards &amp; Honors" style="carbon"]
                        <script> window.dmWebProfiles.showProfile({ container: "#dm-web-profile-awards", clientId: client, reportId: "53dba03d-018e-11ee-8e01-a923555b5d95", userIdentifier: "WebProfileID", WebProfileID: webid, }); profileNull("53dba03d-018e-11ee-8e01-a923555b5d95", "awards");</script>
                        <div id="dm-web-profile-awards"></div>[/su_spoiler] [/su_accordion]
                    </div>
                    <div id="patents">[su_accordion][su_spoiler title="Patents &amp; Copyrights" style="carbon"]
                        <script> window.dmWebProfiles.showProfile({ container: "#dm-web-profile-ip", clientId: client, reportId: "c0f4d868-01a4-11ee-8e01-c579acb588d8", userIdentifier: "WebProfileID", WebProfileID: webid, }); profileNull("c0f4d868-01a4-11ee-8e01-c579acb588d8", "patents");</script>
                        <div id="dm-web-profile-ip"></div>[/su_spoiler] [/su_accordion]
                    </div>
                    <div id="media">[su_accordion][su_spoiler title="Media" style="carbon"]
                        <script> window.dmWebProfiles.showProfile({ container: "#dm-web-profile-media", clientId: client, reportId: "c7786b41-0160-11ee-8e01-13e939e9f659", userIdentifier: "WebProfileID", WebProfileID: webid, }); profileNull("c7786b41-0160-11ee-8e01-13e939e9f659", "media");</script>
                        <div id="dm-web-profile-media"></div>[/su_spoiler] [/su_accordion]
                    </div>
                </div>
            </div>
        </div>
    </div>
</div><!-- /wp:html -->
"""

'''
### student
html_content = """
<!-- wp:html -->
 <div class="chevronProfile color-none"></div>
 <div class="header-profile">
  <div class="heading">
  <div class="faculty__image"><img alt="Closeup of Ila Peeler"
  src="https://biology.sdsu.edu/wp-content/uploads/profiles/ila-peeler-300.jpg"></div>
  <div class="faculty__heading">
  <h1>Ila Peeler, M.S.</h1>
  <p>Pronouns: Ila</p>
  <p class="profileLine"></p>
 <br>
  <p>Doctoral Student<br /></p>
  <p><strong>SDSU / UC San Diego Joint Doctoral Program in Cell and Molecular Biology</strong><br><br></p>
  <p>San Diego</p>
  </div>
  </div>
  <div class="profile-content">
  <script src="https://ackerman.sdsu.edu/_resources_insight_child/js/dm.js"></script>
  <script src="https://ackerman.sdsu.edu/_resources_insight_child/js/hidethis.js"></script>
  <div class="faculty-info">
  <dl class="faculty__contact">
  <div id="email">
  <dt class="email">Email</dt>
  <dd class="faculty__email"><a href="mailto:ipeeler8102@sdsu.edu">ipeeler8102@sdsu.edu</a></dd>
  </div>
  <div id="phone">
  <dt class="phone">Phone</dt>
  <dd class="faculty__phone"><a href="tel:"></a></dd>
  </div>
  <div id="office">
  <dt class="office">Location</dt>
  <dd class="faculty__office">
  <!-- <a href="https://www.google.com/maps/place/6363+Alvarado+Ct,+San+Diego,+CA+92120/@32.7771797,-117.0620524,18.52z/data=!4m6!3m5!1s0x80d956897913f591:0x7bfa7035c51e29c8!8m2!3d32.7768156!4d-117.062353!16s%2Fg%2F11c2ctpdvz?entry=ttu" title="6363 Alvarado Research and Professional Center">ARPC-63</a><a href="https://www.google.com/maps/place/6505+Alvarado+Rd,+San+Diego,+CA+92120/@32.7774196,-117.0604529,18.52z/data=!4m6!3m5!1s0x80d9568bb5541165:0x8b4dc24d5fc07cab!8m2!3d32.7773279!4d-117.0603396!16s%2Fg%2F11c28_bx0h?entry=ttu" title="6505 Alvarado Research and Professional Center">ARPC-65</a><a href="https://map.concept3d.com/?id=801#!m/147063?s/?sbc/" title="Atkinson Hall">ATH</a><a href="https://map.concept3d.com/?id=801#!m/147074" title="Donald P. Shiley BioScience Center">BSCI</a><a href="https://map.concept3d.com/?id=801#!m/147070" title="Chemical Sciences Laboratory">CSL</a><a href="https://map.concept3d.com/?id=801#!m/473833" title="Engineering and Interdisciplinary Sciences Complex">EIS</a><a href="https://map.concept3d.com/?id=801#!m/147082" title="Geology Mathematics Computer Science">GMCS</a><a href="https://map.concept3d.com/?id=801#!m/147088" title="Life Sciences North">LSN</a><a href="https://map.concept3d.com/?id=801#!m/617938" title="Life Science South">LSS</a><a href="https://map.concept3d.com/?id=801#!m/147095" title="Physics">P</a><a href="https://map.concept3d.com/?id=801#!m/147096" title="Physics Astronomy">PA</a><a href="https://map.concept3d.com/?id=801#!m/147094" title="Physical Sciences">PS</a> --><a
  href="https://map.concept3d.com/?id=801#!m/147088" title="Life Science North"
  target="_blank">LSN</a> 311 and 308<br>5500 Campanile Dr<br />San Diego, CA, 92182</dd>
  </div>
  <div id="mailcode">
  <dt class="mail-code">Mail Code</dt>
  <dd class="faculty__mail">4614</dd>
  </div>
  <div id="fax">
  <dt class="fax">Fax</dt>
  <dd class="faculty__phone"></dd>
  </div>
  <div id="links">
  <dt class="links">Links</dt>
  <dd><a href="https://czlab.sdsu.edu/team/" class="faculty__website">Website</a></dd>
  </div>
  <div id="accounts" class="hide">
  <dt class="accounts">Accounts</dt>
  <dd>
  <ul class="sociallinks">
  <li class="linkedin"><a href="https://linkedin.com/">LinkedIn</a></li>
  </ul>
  </dd>
  </div>
  </dl>
  </div>
  <script> contactNull(); </script>
  <div class="content-items">
  <div class="content-expertise">
  <h2>Areas of Expertise</h2>
  <p>Host-Pathogen Interactions, Bioinformatics, Genome-Scale Metabolic Modeling</p>
  </div>
  <div id="content-messages" class="hide">
  <h2>Student Opportunities</h2>
  <ol class="profile-messages">
  <li>Message 1</li>
  <li>Message 2</li>
  </ol>
  </div>
  <div class="content-bio">
  <h2>Bio</h2>
  <p>My main research focus is integrating computational and experimental biology to study host-pathogen
  interactions. I apply genome-scale metabolic modeling to explore the metabolic requirements for
  bacterial infection and colonization in nematodes.</p>
  </div>
  <div>
  <h2>Details</h2>
  <div class="content-details-2"><!-- Education -->
  <div id="education">[su_accordion] [su_spoiler title="Education" style="carbon"]<ol
  class="dm-profile-activities">
  <li class="ea-profile-activity">B.S. Biological Sciences<br />California Polytechnic University, San Luis Obispo</li>
  <li class="ea-profile-activity">M.S. Cellular and Molecular Biology<br />San Diego State University</li>
  </ol>
  <div id="dm-web-profile-education"></div>[/su_spoiler] [/su_accordion]
  </div><!-- Publication -->
  <div id="publications" class="hide">[su_accordion] [su_spoiler title="Publications" style="carbon"]
  <ol class="dm-profile-activities">
  <li class="ea-profile-activity">[A]</li>
  <li class="ea-profile-activity">[B]</li>
  <li class="ea-profile-activity">[C]</li>
  </ol>
  <div id="dm-web-profile-publications"></div>[/su_spoiler] [/su_accordion]
  </div><!-- Presentations -->
  <div id="presentations">[su_accordion] [su_spoiler title="Presentations"
  style="carbon"]<ol class="dm-profile-activities">
  <li class="ea-profile-activity">ASM Microbe â€“ Poster Presentation â€“ Atlanta, June 2024 â€œMetabolic Modeling of the Intracellular Filamenting Bacterium, Bordetella atropiâ€</li>
  <li class="ea-profile-activity">Microbial Ecology and Evolution Hub-based Conference â€“ Poster Presentation â€“ January, 2024 â€œMetabolic modeling of recently discovered pathogenic bacteria, Bordetella atropi</li>
  <li class="ea-profile-activity">24th International C. elegans Conference â€“ Oral Presentation â€“ Glasgow, June 2023 â€œMetabolic modeling and characterization of the nematode-infecting bacterial pathogen, Bordetella atropiâ€</li>
  <li class="ea-profile-activity">37th Annual CSU Student Research Competition â€“ Oral presentation â€“ San Diego, April 2023 â€œUnderstanding the Metabolism of the Recently Isolated Infectious Bacterium, Bordatella atropiâ€</li>
  <li class="ea-profile-activity">2023 SDSU Student Symposium (S3) â€“ Oral presentation â€“ San Diego, March 2023. â€œUnderstanding the Metabolism of the Recently Isolated Infectious Bacterium, Bordatella atropiâ€</li>
  </ol>
  <div id="dm-web-profile-presentations"></div>[/su_spoiler] [/su_accordion]
  </div><!-- Service -->
  <div id="service">[su_accordion] [su_spoiler title="Service" style="carbon"]<ol
  class="dm-profile-activities">
  <li class="ea-profile-activity">Participated in partnership between CZ Lab at San Diego State and Northrop Elementary School to share biological research with 5th Graders.</li>
  </ol>
  <div id="dm-web-profile-service"></div>[/su_spoiler] [/su_accordion]
  </div><!-- Grants -->
  <div id="grants">[su_accordion] [su_spoiler title="Grants" style="carbon"]<ol
  class="dm-profile-activities">
  <li class="ea-profile-activity">The 16th SDSU Student Symposium Presidentâ€™s Award â€“ San Diego, March 2023</li>
  </ol>
  <div id="dm-web-profile-grants"></div>[/su_spoiler] [/su_accordion]
  </div><!-- Clinical -->
  <div id="clinical" class="hide">[su_accordion] [su_spoiler title="Clinical Trials" style="carbon"]
  <ol class="dm-profile-activities">
  <li class="ea-profile-activity">[A]</li>
  <li class="ea-profile-activity">[B]</li>
  <li class="ea-profile-activity">[C]</li>
  </ol>
  <div id="dm-web-profile-clinical"></div>[/su_spoiler] [/su_accordion]
  </div><!-- Awards and Honors -->
  <div id="awards" class="hide">[su_accordion] [su_spoiler title="Awards &amp; Honors" style="carbon"]
  <ol class="dm-profile-activities">
  <li class="ea-profile-activity">[A]</li>
  <li class="ea-profile-activity">[B]</li>
  <li class="ea-profile-activity">[C]</li>
  </ol>
  <div id="dm-web-profile-awards"></div>[/su_spoiler] [/su_accordion]
  </div><!-- Patents and Copyrights -->
  <div id="patents" class="hide">[su_accordion] [su_spoiler title="Patents &amp; Copyrights"
  style="carbon"]<ol class="dm-profile-activities">
  <li class="ea-profile-activity">[A]</li>
  <li class="ea-profile-activity">[B]</li>
  <li class="ea-profile-activity">[C]</li>
  </ol>
  <div id="dm-web-profile-ip"></div>[/su_spoiler] [/su_accordion]
  </div><!-- Media -->
  <div id="media" class="hide">[su_accordion] [su_spoiler title="Media" style="carbon"]<ol
  class="dm-profile-activities">
  <li class="ea-profile-activity">[A]</li>
  <li class="ea-profile-activity">[B]</li>
  <li class="ea-profile-activity">[C]</li>
  </ol>
  <div id="dm-web-profile-media"></div>[/su_spoiler] [/su_accordion]
  </div><!-- Fun Facts -->
  <div id="funfacts">[su_accordion] [su_spoiler title="Fun Facts" style="carbon"]<ol
  class="dm-profile-activities">
  <li class="ea-profile-activity">What is your favorite thing to do with your free time?<br />I love hiking, yoga, reading fiction, drawing and painting!</li>
  </ol>
  <div id="dm-web-profile-funfacts"></div>[/su_spoiler] [/su_accordion]
  </div>
  </div>
  </div>
  </div>
  </div>
 </div><!-- /wp:html -->
"""
'''
soup = BeautifulSoup(html_content, 'html.parser')


# Extract fields
profile_image = soup.select_one('.faculty__image img')['src']
name = soup.select_one('.faculty__heading h1').text.strip()
first_name, last_name, suffix = name.replace(",", "").split()
pronouns = soup.select_one('.faculty__heading p:nth-of-type(1)').text.replace("Pronouns:", "").strip()
title = soup.select_one('.faculty__heading p:nth-of-type(3)')
college_or_program = soup.select_one('.faculty__heading p:nth-of-type(4)')
location = soup.select_one('.faculty__heading p:nth-of-type(5)').text.strip()
email = soup.select_one('.faculty__email a').text.strip() if "hide" not in str(soup.select_one('#email')) else ''
if "hide" not in str(soup.select_one('#office')):
    office_location = soup.select_one('.faculty__office')
    building_and_room = office_location.a.get('title').strip() + " " + office_location.a.next_sibling.strip()
    building, room_number = building_and_room.split(" ")
    street_address = office_location.contents[3].strip()
    city_state_zip = office_location.contents[5].strip()
    city, state_zip = city_state_zip.rsplit(", ", 1)
    state, zip_code = state_zip.split(" ")
else:
    building = ''
    room_number = ''
    street_address = ''
    city = ''
    state = ''
    zip_code = ''
mail_code = soup.select_one('.faculty__mail').text.strip()
website = soup.select_one('.faculty__website')['href']
linkedin = soup.select_one('.sociallinks .linkedin a')['href']
expertise = soup.select_one('.content-expertise p').text.strip()
bio = soup.select_one('.content-bio p').text.strip()


# Extract education details
education_section = soup.select_one('#education')
if education_section:
    education = [
    item.text.strip()
    for item in education_section.select('.ea-profile-activity')
]
else:
    education = []

# Extract presentations
presentations_section = soup.select_one('#presentations')
if presentations_section:
    presentations = [
    item.text.strip()
    for item in presentations_section.select('.ea-profile-activity')
]
else:
    presentations = [] 

# Extract Publication
publications_section = soup.select_one('#publications')
if publications_section:
    publications = [
    item.text.strip()
    for item in publications_section.select('.ea-profile-activity')
]
else:
    publications = []

# Extract service
service_section = soup.select_one('#service')
if service_section:
    service = [
    item.text.strip()
    for item in service_section.select('.ea-profile-activity')
]
else:
    service = []

# Extract clinical
clinical_section = soup.select_one('#clinical')
if clinical_section:
    clinical = [
    item.text.strip()
    for item in clinical_section.select('.ea-profile-activity')
]
else:
    clinical = []

# Extract awards
awards_section = soup.select_one('#awards')
if awards_section:
    awards = [
    item.text.strip()
    for item in awards_section.select('.ea-profile-activity')
]
else:
    awards = []

# Extract patents
patents_section = soup.select_one('#patents')
if patents_section:
    patents = [
    item.text.strip()
    for item in patents_section.select('.ea-profile-activity')
]
else:
    patents = []

# Extract media
media_section = soup.select_one('#media')
if media_section:
    media = [
    item.text.strip()
    for item in media_section.select('.ea-profile-activity')
]
else:
    media = []

# Extract funfacts
funfacts_section = soup.select_one('#funfacts')
if funfacts_section:
    funfacts = [
    item.text.strip()
    for item in funfacts_section.select('.ea-profile-activity')
]
else:
    funfacts = []

# Extract courses
courses_section = soup.select_one('#courses')
if courses_section:
    courses = [
        item.text.strip()
        for item in courses_section.select('.ea-profile-activity')
    ]
else:
    courses = []



# Print extracted fields
print("Profile Image:", profile_image)
print("First Name:", first_name)
print("Last Name:", last_name)
print("Suffix:", suffix)
print("Pronouns:", pronouns)
print("Title:", title)
print("College or Program:", college_or_program)
print("Location:", location)
print("Email:", email)
print("Office Location:", office_location)
print("Mail Code:", mail_code)
print("Website:", website)
print("LinkedIn:", linkedin)
print("Expertise:", expertise)
print("Bio:", bio)
print("Education:", education)
print("Presentations:", presentations)
print("publications:", publications)
print("clinical:", clinical)
print("service:", service)
print("awards:", awards)
print("patents:", patents)
print("media:", media)
print("funfacts:", funfacts)
print("courses:", courses)
print("--------------------------------")