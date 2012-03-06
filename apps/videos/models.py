# richard -- video index system
# Copyright (C) 2012 richard contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.template.defaultfilters import slugify


USE_HTML_HELP_TEXT = "Use HTML."


class Category(models.Model):
    KIND_CONFERENCE = 1
    KIND_PUG = 2

    KIND_CHOICES = (
        (KIND_CONFERENCE, u'Conference'),
        (KIND_PUG, u'Python User Group'),
        )

    kind = models.IntegerField(choices=KIND_CHOICES)

    # e.g. 'PyCon', 'ChiPy', ...
    name = models.CharField(max_length=255)

    # e.g. 'PyCon 2010', 'ChiPy', ...
    title = models.CharField(max_length=255)

    description = models.TextField(blank=True, default=u'',
                                   help_text=USE_HTML_HELP_TEXT)
    url = models.URLField(blank=True, default=u'')
    slug = models.SlugField(unique=True)
    notes = models.TextField(blank=True, default=u'')
    start_date = models.DateField(null=True)

    def __unicode__(self):
        return '<Category %s>' % self.title

    class Meta(object):
        ordering = ["name", "title"]

    @models.permalink
    def get_absolute_url(self):
        return ('category', (self.pk, self.slug))


class Speaker(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return '<Speaker %s: %s>' % (self.id, self.name)

    class Meta(object):
        ordering = ['name']

    @models.permalink
    def get_absolute_url(self):
        return ('speaker', (self.pk, self.slug))


class Tag(models.Model):
    tag = models.CharField(max_length=30)

    def __unicode__(self):
        return '<Tag %s>' % self.tag

    class Meta(object):
        ordering = ['tag']


class Video(models.Model):
    STATE_LIVE = 1
    STATE_DRAFT = 2

    STATE_CHOICES = (
        (STATE_LIVE, u'Live'),
        (STATE_DRAFT, u'Draft'),
        )

    state = models.IntegerField(choices=STATE_CHOICES, null=True)

    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True, default=u'',
                               help_text=USE_HTML_HELP_TEXT)
    description = models.TextField(blank=True, default=u'',
                                   help_text=USE_HTML_HELP_TEXT)
    tags = models.ManyToManyField(Tag)
    category = models.ForeignKey(Category)
    speakers = models.ManyToManyField(Speaker)

    # notes for quality issues (audio or video) in the video
    quality_notes = models.TextField(blank=True, default=u'',
                                     help_text=USE_HTML_HELP_TEXT)

    # text for copyright/license--for now it's loose form.
    # if null, use source video link.
    copyright_text = models.TextField(null=True)

    # embed for flash player things
    embed = models.TextField(null=True, blank=True)

    # url for the thumbnail
    thumbnail_url = models.URLField(max_length=255, null=True)

    # TODO: fix this--there should be one duration in seconds and then
    # each video type should have a filesize

    # TODO: add video_m4v

    # these are downloadable urls
    video_ogv_length = models.IntegerField(null=True)
    video_ogv_url = models.URLField(max_length=255, null=True)
    video_mp4_length = models.IntegerField(null=True)
    video_mp4_url = models.URLField(max_length=255, null=True)
    video_webm_length = models.IntegerField(null=True)
    video_webm_url = models.URLField(max_length=255, null=True)

    # source url in case we need to find things again
    source_url = models.URLField(max_length=255, null=True)

    # whiteboard for editor notes
    whiteboard = models.CharField(max_length=255, blank=True, default=u'')

    # when the video was originally recorded
    recorded = models.DateField(null=True)

    # when the video was added to this site
    added = models.DateTimeField(auto_now_add=True)

    # when the video metadata was last updated
    updated = models.DateTimeField(auto_now=True)

    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return '<Video %s (%s)>' % (self.title[:30], self.category)

    class Meta(object):
        get_latest_by = 'recorded'
        ordering = ['-recorded', 'title']

    @models.permalink
    def get_absolute_url(self):
        return ('video', (self.pk, self.slug))

    def save(self):
        self.slug = slugify(self.title)
        super(Video, self).save()


class RelatedUrl(models.Model):
    video = models.ForeignKey(Video, related_name='related_urls')
    url = models.URLField(max_length=255)
    description = models.CharField(max_length=255, blank=True, default=u'')

    def __unicode__(self):
        return '<URL %s>' % self.url