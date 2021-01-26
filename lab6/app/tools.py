import os
from uuid import uuid4
from flask import url_for, current_app
import hashlib
from werkzeug.utils import secure_filename
from models import Theme, Image, Course

from app import db

class ImageSaver:
    def __init__(self, file):
        self.file = file

    def save(self):
        self.img = self.__find_by_md5_hash()
        if self.img is not None:
            return self.img
        file_name = secure_filename(self.file.filename)
        self.img = Image(
            id=str(uuid4()), 
            file_name=file_name, 
            mime_type=self.file.mimetype, 
            md5_hash=self.md5_hash
        )
        self.file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], self.img.storage_filename))
        db.session.add(self.img)
        db.session.commit()
        return self.img

    def bind_to_object(self, obj):
        self.img.object_type = obj.__tablename__
        self.img.object_id = obj.id
        self.img.active = True
        db.session.add(self.img)
        db.session.commit()

    def __find_by_md5_hash(self):
        self.md5_hash = hashlib.md5(self.file.read()).hexdigest()
        self.file.seek(0)
        return Image.query.filter(Image.md5_hash == self.md5_hash).first()

class CoursesFilter:
    def __init__(self, name, category_ids):
        self.name = name
        self.category_ids = category_ids
        self.query = Course.query

    def perform(self):
        self.__filter_by_name()
        self.__filter_by_category()
        return self.query.order_by(Course.created_at.desc())

    def __filter_by_name(self):
        if self.name:
            self.query = self.query.filter(Course.name.ilike('%' + self.name + '%'))
    
    def __filter_by_category(self):
        if self.category_ids:
            self.query = self.query.filter(Course.category_id.in_(self.category_ids))

class Navigator:
    def __init__(self, course, theme=None, current_step=None):
        self.course = course
        self.theme = theme
        self.current_step = current_step
        self.__next_step = None
        self.__prev_step = None
        self.__init_all_steps()
        if current_step is None:
            self.__init_current_step()

    def __init_all_steps(self):
        self.__all_steps = []
        self.__all_themes = []
        themes = self.course.themes[::-1]
        if not themes:
            return self.__all_steps
        theme = themes.pop()
        while theme is not None:
            self.__all_themes.append(theme)
            if theme.steps:
                self.__all_steps += theme.steps
            if theme.subthemes:
                themes += theme.subthemes[::-1]
            theme = themes.pop() if len(themes) > 0 else None
        return self.__all_steps

    def __init_current_step(self):
        if self.theme:
            steps_themes = [s.theme for s in self.__all_steps]
            if self.theme in steps_themes:
                self.current_step = self.__all_steps[steps_themes.index(self.theme)]
            else:
                theme_index = self.__all_themes.index(self.theme)
                if theme_index < len(self.__all_themes) - 1:
                    next_themes = self.__all_themes[theme_index+1:]
                    next_steps = (s for s in self.__all_steps if s.theme in next_themes)
                    try:
                        self.current_step = next(next_steps)
                    except StopIteration:
                        self.current_step = self.__all_steps[-1] if self.__all_steps else None
                else:
                    self.current_step = self.__all_steps[-1] if self.__all_steps else None
        else:
            self.current_step = self.__all_steps[0] if self.__all_steps else None

    @property
    def next_url(self):
        if self.next_step is None:
            return '#'
        return url_for(
            'courses.show_content', 
            course_id=self.course.id, 
            theme_id=self.next_step.theme.id, 
            step_id=self.next_step.id
        )

    @property
    def prev_url(self):
        if self.prev_step is None:
            return '#'
        return url_for(
            'courses.show_content', 
            course_id=self.course.id, 
            theme_id=self.prev_step.theme.id, 
            step_id=self.prev_step.id
        )

    @property
    def next_step(self):
        if not self.__next_step:
            self.__find_next_step()
        return self.__next_step

    def __find_next_step(self):
        current_index = self.__all_steps.index(self.current_step)
        if current_index < len(self.__all_steps) - 1:
            self.__next_step = self.__all_steps[current_index + 1]
        else:
            self.__next_step = None

    @property
    def prev_step(self):
        if not self.__prev_step:
            self.__find_prev_step()
        return self.__prev_step

    def __find_prev_step(self):
        current_index = self.__all_steps.index(self.current_step)
        if current_index > 0:
            self.__prev_step = self.__all_steps[current_index - 1]
        else:
            self.__prev_step = None