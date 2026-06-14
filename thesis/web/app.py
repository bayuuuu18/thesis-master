"""Thesis Master Web Application - Flask Dashboard."""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from thesis.database import Database
from thesis.config import Config
from thesis.modules.searcher import PaperSearcher
from thesis.modules.reference_manager import ReferenceManager
from thesis.modules.citation import CitationGenerator
from thesis.modules.ai_assistant import AIAssistant
from thesis.modules.project_manager import ProjectManager
from thesis.modules.exporter import ThesisExporter


def create_app(config=None):
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
    app.config['SECRET_KEY'] = os.urandom(24).hex()

    cfg = Config()
    db = Database()
    searcher = PaperSearcher()
    ref_manager = ReferenceManager()
    citation_gen = CitationGenerator()
    ai = AIAssistant()
    project = ProjectManager(db)
    exporter = ThesisExporter(db)

    # Initialize default chapters
    project.init_default_chapters()

    @app.route('/')
    def dashboard():
        progress = project.get_progress()
        milestones = project.get_milestones(pending_only=True)
        todos = project.get_todos(pending_only=True)
        return render_template('dashboard.html',
                             progress=progress,
                             milestones=milestones,
                             todos=todos)

    @app.route('/references')
    def references():
        refs = ref_manager.list_references()
        return render_template('references.html', references=refs)

    @app.route('/search')
    def search_page():
        return render_template('search.html')

    @app.route('/writer')
    def writer():
        chapters = project.get_chapters()
        return render_template('writer.html', chapters=chapters)

    @app.route('/citations')
    def citations():
        return render_template('citations.html')

    @app.route('/settings')
    def settings():
        return render_template('settings.html', config=cfg.get_config())

    # --- API Routes ---
    @app.route('/api/search', methods=['POST'])
    def api_search():
        data = request.json
        query = data.get('query', '')
        source = data.get('source', 'arxiv')
        limit = data.get('limit', 10)
        try:
            results = searcher.search(query, source=source, max_results=limit)
            return jsonify({'success': True, 'results': results})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/references', methods=['GET'])
    def api_references():
        refs = ref_manager.list_references()
        return jsonify({'references': refs})

    @app.route('/api/references', methods=['POST'])
    def api_add_reference():
        data = request.json
        try:
            ref_id = ref_manager.add_reference(**data)
            return jsonify({'success': True, 'id': ref_id})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/references/<int:ref_id>', methods=['DELETE'])
    def api_delete_reference(ref_id):
        ref_manager.delete_reference(ref_id)
        return jsonify({'success': True})

    @app.route('/api/cite', methods=['POST'])
    def api_cite():
        data = request.json
        doi = data.get('doi', '')
        style = data.get('style', 'apa')
        try:
            citation = citation_gen.from_doi(doi, style=style)
            return jsonify({'success': True, 'citation': citation})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/ai/summarize', methods=['POST'])
    def api_ai_summarize():
        data = request.json
        text = data.get('text', '')
        try:
            summary = ai.summarize(text)
            return jsonify({'success': True, 'summary': summary})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/ai/paraphrase', methods=['POST'])
    def api_ai_paraphrase():
        data = request.json
        text = data.get('text', '')
        try:
            result = ai.paraphrase(text)
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/ai/review', methods=['POST'])
    def api_ai_review():
        data = request.json
        topic = data.get('topic', '')
        try:
            refs = ref_manager.list_references()
            review = ai.generate_literature_review(topic, refs[:10])
            return jsonify({'success': True, 'review': review})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/chapters', methods=['GET'])
    def api_chapters():
        chapters = project.get_chapters()
        return jsonify({'chapters': chapters})

    @app.route('/api/chapters/<int:ch_id>', methods=['PUT'])
    def api_update_chapter(ch_id):
        data = request.json
        project.update_chapter(ch_id, **data)
        return jsonify({'success': True})

    @app.route('/api/todos', methods=['GET'])
    def api_todos():
        todos = project.get_todos(pending_only=False)
        return jsonify({'todos': todos})

    @app.route('/api/todos', methods=['POST'])
    def api_add_todo():
        data = request.json
        todo_id = project.add_todo(
            task=data.get('task', ''),
            priority=data.get('priority', 'medium'),
            due_date=data.get('due_date')
        )
        return jsonify({'success': True, 'id': todo_id})

    @app.route('/api/todos/<int:todo_id>/complete', methods=['POST'])
    def api_complete_todo(todo_id):
        project.complete_todo(todo_id)
        return jsonify({'success': True})

    @app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
    def api_delete_todo(todo_id):
        project.delete_todo(todo_id)
        return jsonify({'success': True})

    @app.route('/api/export/<format>', methods=['POST'])
    def api_export(format):
        data = request.json or {}
        output = data.get('output', f'thesis_export.{format}')
        try:
            if format == 'docx':
                exporter.export_docx(output, data.get('metadata'))
            elif format == 'md':
                exporter.export_markdown(output, data.get('metadata'))
            elif format == 'tex':
                exporter.export_latex(output, data.get('metadata'))
            elif format == 'bib':
                exporter.export_bibtex(output)
            return jsonify({'success': True, 'path': output})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/progress', methods=['GET'])
    def api_progress():
        return jsonify(project.get_progress())

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
