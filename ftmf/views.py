# views.py
from django.shortcuts import render, redirect, reverse
from .models import Staff, Subject, Section, Timetable
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Prefetch
from django.contrib import messages
from PIL import Image, ImageDraw, ImageFont
import os
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS

import os
from django.conf import settings
# For flutter. Don't touch. #

from rest_framework.generics import ListAPIView
from .serializers import SubSerializer
from rest_framework import permissions

class SubList(ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
# For flutter ends #


def master_timetable(request):
    # Fetch all staff
    all_staff = Staff.objects.all()

    # Create a directory to store timetable images temporarily
    temp_image_dir = "/tmp/staff_timetable_images/"
    if not os.path.exists(temp_image_dir):
        os.makedirs(temp_image_dir)

    # List to hold the paths of generated images
    image_paths = []

    # Process each staff member's timetable
    for staff in all_staff:
        name = staff.name
        _id = staff.id

        # Convert timetable to dummy format
        dummy_timetable = convert_to_dummy_timetable(get_timetable(name, _id))

        # Check if name is section or staff and generate timetable image
        sec, yr, sem = is_section_1_staff_0_nun_m1(name, _id)
        noff = "Faculty" if sec == 1 else "Section"
        section = name

        # Generate a unique filename for each staff member
        filename = f"{temp_image_dir}timetable_{name}_{_id}.png"

        # Generate the timetable image
        image_path = generate_timetable_image(dummy_timetable, filename=filename, noff=noff, section=section, _id=_id)
        image_paths.append(image_path)

    # Create HTML content with the images
    html_content = render_to_string('all_staff_timetables.html', {'image_paths': image_paths})

    # Generate PDF from the HTML content
    pdf_file_path = f"{temp_image_dir}all_staff_timetables.pdf"
    HTML(string=html_content).write_pdf(pdf_file_path, stylesheets=[CSS(string='img { width: 100%; height: auto; }')])

    # Serve the generated PDF file
    with open(pdf_file_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="all_staff_timetables.pdf"'
        return response

    # Clean up temporary files
    for image_path in image_paths:
        os.remove(image_path)
    os.rmdir(temp_image_dir)

def is_section_1_staff_0_nun_m1(name, _id):
    """
    Return
    1: if name is section
    0: if name is staff
    -1: if name is not found
    """
    staff_dict = {s["name"]: s["id"] for s in Staff.objects.values("id", "name")}
    section_dict = {s["name"]: s["id"] for s in Section.objects.values("id", "name")}

    _section = False
    if name in section_dict:
        _section = True

    # Prefetch related objects to minimize database hits
    if _section:
        rows = Timetable.objects.filter(section=_id).select_related('subject', 'staff')
    else:
        rows = Timetable.objects.filter(staff=_id).select_related('subject', 'section')

    for row in rows:
        if _section:
          return 1,row.section.year, row.section.semester
        else:
            return 0,row.staff.name, None


    if _section:
        vs = Section.objects.filter(id=_id)[0]
        return 1, vs.year, vs.semester
    else:

        return 0, None, None
def get_timetable(name, _id):
    #timetable = {"Monday":{}, "Tuesday":{}, "Wednesday":{}, "Thursday":{}, "Friday":{}, "Saturday":{}}
    #dictionary comprehension, same as above
    timetable = {day: {i: "" for i in range(1, 13)} for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]}

    '''staff = [s["name"] for s in Staff.objects.all().values()]
    section = [s["name"] for s in Section.objects.all().values()]
    staff_ids = [s["id"] for s in Staff.objects.all().values()]
    section_ids = [s["id"] for s in Section.objects.all().values()]'''
    # Get all staff and section names and ids in a dictionary for better lookup
    staff_dict = {s["name"]: s["id"] for s in Staff.objects.values("id", "name")}
    section_dict = {s["name"]: s["id"] for s in Section.objects.values("id", "name")}

    _section = False
    if name in section_dict:
        _section = True
    elif name in staff_dict:
        pass
    else:
        return timetable  # Return an empty timetable if the name is not found

    # Prefetch related objects to minimize database hits
    if _section:
        rows = Timetable.objects.filter(section=_id).select_related('subject', 'staff')
    else:
        rows = Timetable.objects.filter(staff=_id).select_related('subject', 'section')

    for row in rows:
        if _section:
            timetable[row.day][row.time_slot] = f"{row.subject.name}, {row.staff.name}"
        else:
            timetable[row.day][row.time_slot] = f"{row.subject.name}, {row.section.year}-{row.section.semester} {row.section.name}"

    return timetable




def generate_timetable_image(timetable, filename="timetable.png", show_image = False,noff = "Faculty",sem = "II",section = "AIML",_id=1 ,year = "II",college  = "JNTUH University College of Engineering, Science & Technology, Hyderabad",dept = "Dept of Computer Science and Engineering",name = "PROVISIONAL TIME-TABLE",no = 216,dt = "19/02/2023"):
    # Separate subjects and staff
    subjects = {day: {slot: value.split(",")[0].strip() if value else "..." for slot, value in slots.items()} for day, slots in timetable.items()}
    staff = {day: {slot: value.split(",")[1].strip() if value else "" for slot, value in slots.items()} for day, slots in timetable.items()}

    sts = {}
    for day, slots in timetable.items():
        for val, sl in slots.items():
            slot = sl.split(",")
            if len(slot) < 2:
                continue
            if slot[0] in sts:
                sts[slot[0]] += "," + slot[1]
            else:
                sts[slot[0]] = slot[1]
    for s in sts:
        st = sts[s].split(",")
        st = set(st)
        sts[s] = ",".join(st)

    # Constants
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    TIME_SLOTS = ["09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "Lunch", "01:45", "02:15", "02:45", "03:15", "03:45", "04:15"]

    # Image dimensions
    img_width = 1502
    img_height = 1000

    # Create a new image with white background
    img = Image.new('RGB', (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    # Load a font
    try:
        font = ImageFont.truetype("/home/FacultyTimetable/FTimetable/ftmf/times new roman.ttf", 18)
        header_font = ImageFont.truetype("/home/FacultyTimetable/FTimetable/ftmf/times new roman bold.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()
    if is_section_1_staff_0_nun_m1(section, _id)[0] == 1:
        college_details = [
            college,
            dept,
            f"B.Tech. {year}-Year (Section - {section}) ({sem}-Semester)",
            name,
        ]
    else:
        college_details = [
            college,
            dept,
            f"{section}'s timetable",
        ]
    y_offset = 10
    for line in college_details:
        text_width = draw.textlength(line, font=header_font)
        text_height = draw.textbbox((0, 0), line, font=header_font)[3] - draw.textbbox((0, 0), line, font=header_font)[1]
        draw.text(((img_width - text_width) / 2, y_offset), line, font=header_font, fill="black")
        y_offset += text_height + 10


    # Column widths and row heights
    col_width = 100
    row_height = 50

    # Draw the header row for time slots
    x_offset = 200
    draw.rectangle([(0, y_offset), (200, y_offset+row_height)],outline="black")
    draw.rectangle([(x_offset, y_offset), (x_offset + col_width * len(TIME_SLOTS), y_offset + row_height)], outline="black")
    for i, slot in enumerate(TIME_SLOTS):
        if i == 6:
            draw.text((x_offset + i * col_width + 10, y_offset + 10), slot, font=font, fill="black")

    for i, slot in enumerate(["9:30 - 11:00", "11:00 - 12:30"]):
        draw.rectangle([(x_offset + i *3* col_width, y_offset), (x_offset + (i+1) *3* col_width, y_offset + row_height)], outline="black")
        draw.text((x_offset + i *3* col_width + 60, y_offset + 10), slot, font=font, fill="black")

    for i, slot in enumerate(["1:45 - 3:15", "3:15 - 4:15"]):
        draw.rectangle([(x_offset + (i)*3*col_width + 7*col_width, y_offset), (x_offset + (i+1)*3*col_width + 7*col_width, y_offset + row_height)], outline="black")
        draw.text((x_offset + (i)*3*col_width + 7*col_width + 60, y_offset + 10), slot, font=font, fill="black")
    # Draw the days column
    y_offset += row_height
    draw.rectangle([(0, y_offset), (200, y_offset + row_height * len(DAYS))], outline="black")
    for i, day in enumerate(DAYS):
        draw.rectangle([(0, y_offset + i * row_height), (200, y_offset + (i + 1) * row_height)], outline="black")
        text_width = draw.textlength(day.upper(), font=header_font)
        text_height = draw.textbbox((0, 0), day, font=header_font)[3] - draw.textbbox((0, 0), day, font=header_font)[1]
        draw.text(((200 - text_width) / 2, y_offset + i * row_height + (row_height - text_height) / 2), day.upper(), font=font, fill="black")

    # Draw the timetable cells with merged slots
    x_offset -= col_width
    for i, day in enumerate(DAYS):
        prev_subject = None
        start_slot = 0
        for j in range(1, 8):
            if j in subjects[day] and subjects[day][j] == prev_subject and j!=7:
                continue
            if prev_subject is not None:
                x = x_offset + start_slot * col_width
                y = y_offset + i * row_height
                draw.rectangle([(x, y), (x + col_width * (j - start_slot), y + row_height)], outline="black")
                text_width = draw.textlength(prev_subject, font=font)
                text_height = draw.textbbox((0, 0), prev_subject, font=font)[3] - draw.textbbox((0, 0), prev_subject, font=font)[1]
                draw.text((x + (col_width * (j - start_slot) - text_width) / 2, y + (row_height - text_height) / 2), prev_subject, font=font, fill="black")
            prev_subject = subjects[day][j] if j in subjects[day] else "..."
            start_slot = j
    x_offset += col_width//2
    for i in range(5):
        x = x_offset + 7 * col_width
        y = y_offset + i * row_height + row_height
        draw.text((x,y), str("LUNCH")[i], font=font, fill="black")
    x_offset += col_width//2
    for i, day in enumerate(DAYS):
        prev_subject = None
        start_slot = 0
        for j in range(7, 14):
            if j in subjects[day] and subjects[day][j] == prev_subject:
                continue
            if prev_subject is not None:
                x = x_offset + start_slot * col_width
                y = y_offset + i * row_height
                draw.rectangle([(x, y), (x + col_width * (j - start_slot), y + row_height)], outline="black")
                text_width = draw.textlength(prev_subject, font=font)
                text_height = draw.textbbox((0, 0), prev_subject, font=font)[3] - draw.textbbox((0, 0), prev_subject, font=font)[1]
                draw.text((x + (col_width * (j - start_slot) - text_width) / 2, y + (row_height - text_height) / 2), prev_subject, font=font, fill="black")
            prev_subject = subjects[day][j] if j in subjects[day] else "..."
            start_slot = j
    # List all subjects and staff side by side below the timetable
    y_offset += row_height * len(DAYS) + 70
    draw.text((30, y_offset), "Name of the Subjects", font=header_font, fill="black")


    draw.text((img_width / 2 + 10, y_offset), f"Name of the {noff}", font=header_font, fill="black")
    y_offset += 30

    subject_names = sorted({subject for day in subjects.values() for subject in day.values() if subject != "..."})
    faculty_names = sorted({name for day in staff.values() for name in day.values() if name})

    max_length = max(len(subject_names), len(faculty_names))

    for i in range(max_length):
        if i < len(subject_names):
            subject_text = f"{i + 1}. {subject_names[i]}"
            line = subject_text
            text_width = draw.textlength(line, font=header_font)
            text_height = draw.textbbox((0, 0), line, font=header_font)[3] - draw.textbbox((0, 0), line, font=header_font)[1]
            draw.text((30, y_offset), subject_text, font=font, fill="black")
        if i < len(subject_names):
            faculty_text = f"{i + 1}. {sts[subject_names[i]]}"
            line = faculty_text
            text_width = draw.textlength(line, font=header_font)
            text_height = draw.textbbox((0, 0), line, font=header_font)[3] - draw.textbbox((0, 0), line, font=header_font)[1]
            draw.text((img_width / 2 + 10, y_offset), faculty_text, font=font, fill="black")
        y_offset += 20

    media_root = settings.MEDIA_ROOT
    # Define a subdirectory within MEDIA_ROOT to save images
    save_directory = os.path.join(media_root, 'images')

    # Ensure the directory exists; create if it doesn't
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    save_path = os.path.join(save_directory, filename)
    img.save(save_path)
    #print(f"Timetable image saved as {image_path}")

    # # Optionally show image
    # if show_image:
    #     image.show()

    return save_path

def convert_to_dummy_timetable(timetable):
    dummy_timetable = {
        "Monday": {i: "" for i in range(1, 13)},
        "Tuesday": {i: "" for i in range(1, 13)},
        "Wednesday": {i: "" for i in range(1, 13)},
        "Thursday": {i: "" for i in range(1, 13)},
        "Friday": {i: "" for i in range(1, 13)},
        "Saturday": {i: "" for i in range(1, 13)},
    }

    for day, slots in timetable.items():
        for slot, content in slots.items():
            if content:
                subject_staff = content.split(", ")
                subject = subject_staff[0]
                staff = subject_staff[1]
                dummy_timetable[day][slot] = f"{subject}, {staff}"

    return dummy_timetable

# Example usage:
# Assuming `timetable` is the output from `get_timetable`
# timetable = get_timetable("Some Name")
# dummy_timetable = convert_to_dummy_timetable(timetable)

# Django view function
def timetable_image_view(request, name = None, _id = None):
    dummy_timetable = convert_to_dummy_timetable(get_timetable(name, _id))


    sec, yr, sem = is_section_1_staff_0_nun_m1(name, _id)
    noff = "Faculty" if sec == 1 else "Section"
    section = name
    # Generate timetable image
    if sec: # if name is section
        image_path = generate_timetable_image(dummy_timetable, filename="timetable.png", noff = noff, section = section, _id=_id, year = yr, sem = sem)
    else:# if name is staff
        image_path = generate_timetable_image(dummy_timetable, filename="timetable.png", noff = noff, section = section,_id=_id)

    image_path = "/"+"/".join(image_path.split("/")[-3:])
    # Render template with image path
    context = {
        'image_path': image_path,
    }
    return render(request, 'timetable_image.html', context)


def home(request):
    sections = Section.objects.all()
    staffs = Staff.objects.all()
    subjects = Subject.objects.all()

    context = {
        'sections': sections,
        'staffs': staffs,
        'subjects': subjects,
    }

    return render(request, 'timetable.html', context)

def staff_timetable(request, staff_id= None):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')

    if staff_id:
        staff = get_object_or_404(Staff, id=staff_id)

    else:
        return HttpResponse("Illegal Entry", status=400)

    sections = Section.objects.all()
    subjects = Subject.objects.all()
    context = {
        'sections': sections,
        'staff': staff,
        'subjects': subjects,
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'times': list(range(1, 13)),  # [1, 2, 3, ..., 12]
        "slots":["9:30","10:00","10:30","11:00","11:30","12:00","1:45","2:15","2:45","3:15","3:45","4:15"],
        'timetable': get_timetable(staff.name, staff_id),
    }

    return render(request, 'staff_timetable.html', context)

def section_timetable(request, section_id = None):
    if request.method == 'POST':
        section_id = request.POST.get('section_id')

    if section_id:
        section = get_object_or_404(Section, id=section_id)
    else:
        return HttpResponse("Illegal Entry", status=400)

    staffs = Staff.objects.all()
    subjects = Subject.objects.all()
    preferences = {stf:",".join([subj.name for subj in stf.subjects.all()]) for stf in staffs},
    context = {
        'section': section,
        'staffs': staffs,
        'sub_preferences': preferences,
        'subjects': subjects,
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'times': list(range(1, 13)),  # [1, 2, 3, ..., 12]
        "slots": ["9:30", "10:00", "10:30", "11:00", "11:30", "12:00", "1:45", "2:15", "2:45", "3:15", "3:45", "4:15"],
        'timetable': get_timetable(section.name, section_id),
    }
    return render(request, 'section_timetable.html', context)

# to be removed later
def create_timetable_instance_from_staff_timetable(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        time_slot = request.POST.get('time_slot')
        subject_id = request.POST.get('subject_id')
        staff_id = request.POST.get('staff_id')
        section_id = request.POST.get('section_id')

        # Check if all necessary POST data is provided
        if not all([day, time_slot, subject_id, staff_id, section_id]):
            return HttpResponse("Missing required fields", status=400)

        # Use get_object_or_404 for better error handling
        subject = get_object_or_404(Subject, id=subject_id)
        staff = get_object_or_404(Staff, id=staff_id)
        section = get_object_or_404(Section, id=section_id)

        # Create the timetable instance
        Timetable.objects.create(
            day=day,
            time_slot=time_slot,
            section=section,
            subject=subject,
            staff=staff,
            availability=1
        )

        # Redirect to the section timetable page
        return redirect(reverse("staff_timetable",  kwargs={'staff_id': staff_id}))

    # If the request method is not POST, return a method not allowed response
    return HttpResponse("Method not allowed", status=405)


def create_timetable_instance_from_section_timetable(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        time_slot = request.POST.get('time_slot')
        subject_id = request.POST.get('subject_id')
        staff_id = request.POST.get('staff_id')
        section_id = request.POST.get('section_id')

        # Check if all necessary POST data is provided
        if not all([day, time_slot, subject_id, staff_id, section_id]):
            return HttpResponse("Missing required fields", status=400)

        # Use get_object_or_404 for better error handling
        subject = get_object_or_404(Subject, id=subject_id)
        staff = get_object_or_404(Staff, id=staff_id)
        section = get_object_or_404(Section, id=section_id)

        # Check if the staff is already assigned to a class at the given day and time slot
        existing_timetable = Timetable.objects.filter(day=day, time_slot=time_slot, staff=staff).first()
        if existing_timetable:
            assigned_subject = existing_timetable.subject
            assigned_section = existing_timetable.section
            messages.success(request,f"Staff already assigned to {assigned_subject.name} in section {assigned_section.year}-{assigned_section.semester} {assigned_section.name} at this time")

            '''return HttpResponse(
                f"Staff already assigned to {assigned_subject.name} in section {assigned_section.name} at this time",
                status=400
            )'''
            return redirect(reverse("section_timetable", kwargs={'section_id':section_id}))

        # Create the timetable instance
        Timetable.objects.create(
            day=day,
            time_slot=time_slot,
            section=section,
            subject=subject,
            staff=staff,
            availability=1
        )

        # Redirect to the section timetable page
        return redirect(reverse("section_timetable", kwargs={'section_id': section_id}))

    # If the request method is not POST, return a method not allowed response
    return HttpResponse("Method not allowed", status=405)

# to be removed later
def delete_timetable_instance_from_staff_timetable(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        time_slot = request.POST.get('time_slot')
        data = request.POST.get('data')
        staff_id = request.POST.get('staff_id')
        subject_name, section_name = data.split(',')
        section_name = section_name.strip()
        section = Section.objects.get(name=section_name)
        staff = Staff.objects.get(id=staff_id)
        subject = Subject.objects.get(name=subject_name)

        Timetable.objects.filter(day=day, time_slot=time_slot, staff=staff, section=section, subject=subject, availability=1).delete()

        return redirect(reverse("staff_timetable",  kwargs={'staff_id': staff_id}))

def delete_timetable_instance_from_section_timetable(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        time_slot = request.POST.get('time_slot')
        data = request.POST.get('data')
        section_id = request.POST.get('section_id')

        # Validate that all necessary POST data is provided
        if not all([day, time_slot, data, section_id]):
            return HttpResponse("Missing required fields", status=400)

        try:
            subject_name, staff_name = data.split(',')
            staff_name = staff_name.strip()
            section_id = int(section_id)  # Ensure section_id is an integer

            staff = get_object_or_404(Staff, name=staff_name)
            section = get_object_or_404(Section, id=section_id)
            subject = get_object_or_404(Subject, name=subject_name)

            for i in range(int(time_slot), 13):
                # Query the Timetable objects
                matching_objects = Timetable.objects.filter(
                    day=day,
                    time_slot=str(i),
                    staff=staff,
                    section=section,
                    subject=subject,
                    availability=1
                )

                # Check if the query returned any objects
                if not matching_objects.exists():
                    break

                # Delete the matching Timetable instance(s)
                matching_objects.delete()


            return redirect(reverse("section_timetable", kwargs={'section_id': section_id}))

        except ValueError: # if section_id cannot be converted to integer
            return HttpResponse("Invalid data format", status=400)
        except Staff.DoesNotExist:
            return HttpResponse("Staff not found", status=404)
        except Section.DoesNotExist:
            return HttpResponse("Section not found", status=404)
        except Subject.DoesNotExist:
            return HttpResponse("Subject not found", status=404)

    # If the request method is not POST, return a method not allowed response
    return HttpResponse("Method not allowed", status=405)

def staff_list(request):
    query = request.GET.get('query', '').strip()  # Get and strip any extra spaces
    if query:
        staff_list = Staff.objects.filter(name__icontains=query)
    else:
        staff_list = Staff.objects.all()

    context = {
        'staffs': staff_list,
        'query': query,
    }
    return render(request, 'staff_list.html', context)

def add_staff(request):
    if request.method == 'POST':
        name = request.POST.get('staff_name')
        if not name:
            # Handle the case where name is not provided
            messages.error(request, "Staff name not provided")
            return redirect('staff_list')
        if Staff.objects.filter(name=name).exists():
            # Handle the case where a staff member with the same name already exists
            messages.error(request, f'Staff member with the name "{name}" already exists.')
            return redirect('staff_list')
        try:
            Staff.objects.create(name=name)
            messages.success(request, f'Staff member "{name}" added successfully.')
            return redirect('staff_list')
        except IntegrityError:
            return HttpResponse("error: Failed to add staff")
    return redirect('staff_list')

def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    name = staff.name
    staff.delete()
    messages.success(request, f'Staff member "{name}" deleted successfully.')
    return redirect('staff_list')

def add_subject(request, staff_id):
    '''
    This view function adds a PREFERRED SUBJECT of the staff,
    creating a many-to-many relation between the staff and subject models.
    '''
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name').strip()
        if subject_name:
            staff_instance = get_object_or_404(Staff, id=staff_id)
            try:
                subject_instance, created = Subject.objects.get_or_create(name=subject_name)
                if staff_instance.subjects.filter(id=subject_instance.id).exists():
                    messages.error(request, f'Subject "{subject_name}" is already added to {staff_instance.name}.')
                else:
                    staff_instance.subjects.add(subject_instance)
                    if created:
                        messages.success(request, f'Subject "{subject_name}" created and added to {staff_instance.name}.')
                    else:
                        messages.success(request, f'Subject "{subject_name}" added to {staff_instance.name}.')
            except Exception as e:
                messages.error(request, f'Error adding subject: {e}')
        else:
            messages.error(request, 'Subject name cannot be empty.')
        return redirect('staff_list')
    return render(request, 'add_subject.html')

def remove_subject(request):
    '''
    This view function removes a PREFERRED SUBJECT from the staff,
    removing a many-to-many realtion between the staff and subject models.
    '''
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        subject_id = request.POST.get('subject_id')

        # Get the staff and subject instances
        staff_instance = get_object_or_404(Staff, id=staff_id)
        subject_instance = get_object_or_404(Subject, id=subject_id)

        try:
            # Remove the subject from the staff's preferred subjects
            staff_instance.subjects.remove(subject_instance)
            messages.success(request, f'Subject "{subject_instance.name}" removed from {staff_instance.name}.')
        except Exception as e:
            messages.error(request, f'Error removing subject: {e}')

    return redirect("staff_list")

def display_all_data(request):
    staff = Staff.objects.all()
    Subs  = Subject.objects.all()
    sections = Section.objects.all()
    return render(request, 'display_all_data.html', {'staff': staff, 'subs': Subs, 'sections':sections})

# to be removed later
def add_section(request, staff_id):
    if request.method == 'POST':
        section_name = request.POST.get('section_name')
        staff_instance = Staff.objects.get(id=staff_id)
        staff_instance.add_section(section_name)
        return redirect('staff_list')
    return render(request, 'add_section.html')

# to be removed later
def remove_section(request, staff_id, section_id):
    staff_instance = get_object_or_404(Staff, id=staff_id)
    staff_instance.remove_section(section_id)
    return redirect('staff_list')

# to be inspected later (doubted as being unnecessary)
def search_staff(request):
    query = request.GET.get('query')
    if query:
        staff = Staff.objects.filter(name__icontains=query)
    else:
        staff = Staff.objects.none()
    return render(request, 'search_results.html', {'staff': staff})

def subject_list(request):
    query = request.GET.get('query')
    if query:
        subject_list = Subject.objects.filter(name__icontains=query)
    else:
        subject_list = Subject.objects.all()

    context = {
        'subjects': subject_list,
        'query': query,
    }
    return render(request, 'subject_list.html', context)

def section_list(request):
    query = request.GET.get('query')
    if query:
        section_list = Section.objects.filter(name__icontains=query)
    else:
        section_list = Section.objects.all()

    context = {
        'sections': section_list,
        'query': query,
    }

    return render(request, 'section_list.html', context)

def delete_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        if not subject_id :
            return HttpResponse("could not recieve subject_id")
        else:
            subject_instance = get_object_or_404(Subject, id=subject_id)

        try:
            subject_name = subject_instance.name
            subject_instance.delete()
            messages.success(request, f'Subject "{subject_name}" deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting subject: {e}')

    return redirect("subject_list")

def delete_section(request):
    if request.method == 'POST':
        section_id = request.POST.get('section_id')
        if not section_id :
            return HttpResponse("could not recieve section_id")
        else:
            section_instance = get_object_or_404(Section, id=section_id)

        try:
            section_name = section_instance.name
            year = section_instance.year
            semester = section_instance.semester
            section_instance.delete()
            messages.success(request, f'Section "{section_name} {year}-{semester}" deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting section: {e}')

    return redirect("section_list")

def create_subject(request):
    if request.method == 'POST':
        name = request.POST.get('subject_name')
        if not name:
            # Handle the case where name is not provided
            messages.error("subject name not provided")
            return redirect('subject_list')
        if Subject.objects.filter(name=name).exists():
            # Handle the case where a subject with the same name already exists
            messages.error(request, f'Subject with the name "{name}" already exists.')
            return redirect('subject_list')
        try:
            Subject.objects.create(name=name)
            messages.success(request, f'Subject "{name}" added successfully.')
            return redirect('subject_list')
        except IntegrityError:
            return HttpResponse(f"error: Failed to add subject: {name}")
    return redirect('subject_list')

def create_section(request):
    if request.method == 'POST':
        name = request.POST.get('section_name')
        year = request.POST.get('year')
        semester = request.POST.get('semester')
        if not name or not year or not semester:
            # Handle the case where field is not provided
            messages.error("section field not provided")
            return redirect('section_list')
        if Section.objects.filter(name=name, year=year,semester=semester).exists():
            # Handle the case where a subject with the same name already exists
            messages.error(request, f'Section with the name "{name} {year}-{semester}" already exists.')
            return redirect('subject_list')
        try:
            Section.objects.create(name=name,year=year,semester=semester)
            messages.success(request, f'Section {name} {year}-{semester} created successfully.')
            return redirect('section_list')
        except IntegrityError:
            return HttpResponse(f"error: Failed to add section:{name} {year}-{semester}")
    return redirect('section_list')



