#!/usr/bin/env python3
"""Thesis Master — All-in-One Thesis Toolkit CLI."""

import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(
        prog='thesis-master',
        description='🎓 Thesis Master — All-in-One Thesis Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python thesis_master.py search "machine learning" --source arxiv --limit 10
  python thesis_master.py cite 10.1038/s41586-020-2649-2 --style apa
  python thesis_master.py manage init
  python thesis_master.py manage progress
  python thesis_master.py serve
        """
    )

    sub = parser.add_subparsers(dest='command', help='Commands')

    # Search
    sp_search = sub.add_parser('search', help='Cari paper dari arXiv/Semantic Scholar/CrossRef')
    sp_search.add_argument('query', help='Query pencarian')
    sp_search.add_argument('--source', choices=['arxiv', 'semantic_scholar', 'crossref', 'all'], default='arxiv')
    sp_search.add_argument('--limit', type=int, default=10)
    sp_search.add_argument('--save', action='store_true', help='Simpan hasil ke referensi')

    # Cite
    sp_cite = sub.add_parser('cite', help='Generate sitasi dari DOI')
    sp_cite.add_argument('doi', help='DOI paper')
    sp_cite.add_argument('--style', choices=['apa', 'ieee', 'chicago', 'harvard', 'vancouver'], default='apa')

    # Manage
    sp_manage = sub.add_parser('manage', help='Kelola project skripsi')
    sp_manage.add_argument('action', choices=['init', 'progress', 'todo', 'milestone', 'chapters'])
    sp_manage.add_argument('args', nargs='*')
    sp_manage.add_argument('--priority', choices=['low', 'medium', 'high'], default='medium')
    sp_manage.add_argument('--due', help='Deadline (YYYY-MM-DD)')

    # Write
    sp_write = sub.add_parser('write', help='Tulis bab skripsi')
    sp_write.add_argument('--chapter', type=int, required=True, help='Nomor bab (1-5)')
    sp_write.add_argument('--content', help='Content (atau gunakan stdin)')

    # Export
    sp_export = sub.add_parser('export', help='Export skripsi ke DOCX/PDF/LaTeX/MD')
    sp_export.add_argument('format', choices=['docx', 'pdf', 'tex', 'md', 'bib'])
    sp_export.add_argument('--output', '-o', help='Output file path')
    sp_export.add_argument('--title', default='Judul Skripsi')
    sp_export.add_argument('--author', default='Nama Mahasiswa')
    sp_export.add_argument('--university', default='Universitas')

    # AI
    sp_ai = sub.add_parser('ai', help='AI assistant features')
    sp_ai.add_argument('action', choices=['summarize', 'paraphrase', 'review'])
    sp_ai.add_argument('text', nargs='?', help='Text to process (or use --file)')
    sp_ai.add_argument('--file', '-f', help='Read text from file')
    sp_ai.add_argument('--topic', help='Topic for literature review')

    # Serve
    sp_serve = sub.add_parser('serve', help='Launch web dashboard')
    sp_serve.add_argument('--port', type=int, default=5000)
    sp_serve.add_argument('--host', default='127.0.0.1')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        console = Console()
        HAS_RICH = True
    except ImportError:
        console = None
        HAS_RICH = False

    from thesis.config import Config
    from thesis.database import Database

    cfg = Config()
    db = Database()

    if args.command == 'search':
        from thesis.modules.searcher import PaperSearcher
        searcher = PaperSearcher()
        if HAS_RICH:
            console.print(f"[bold blue]🔍 Mencari:[/] {args.query} ({args.source})")
        else:
            print(f"🔍 Mencari: {args.query} ({args.source})")
        results = searcher.search(args.query, source=args.source, limit=args.limit)

        if HAS_RICH:
            table = Table(title=f"Hasil Pencarian: {args.query}")
            table.add_column("#", width=3)
            table.add_column("Judul", max_width=50)
            table.add_column("Penulis", max_width=30)
            table.add_column("Tahun", width=5)
            for i, r in enumerate(results, 1):
                table.add_row(str(i), getattr(r, 'title', '')[:50],
                    (getattr(r, 'authors', '') or '')[:30], str(getattr(r, 'year', '')))
            console.print(table)
        else:
            for i, r in enumerate(results, 1):
                print(f"{i}. {getattr(r, 'title', '')} ({getattr(r, 'year', '')}) - {getattr(r, 'authors', '')}")

        if args.save:
            from thesis.modules.reference_manager import ReferenceManager
            rm = ReferenceManager(db)
            for r in results:
                rm.add_reference(title=getattr(r, 'title', ''), authors=getattr(r, 'authors', ''),
                    year=getattr(r, 'year', ''), doi=getattr(r, 'doi', ''), journal=getattr(r, 'source', ''))
            if HAS_RICH:
                console.print(f"[green]✅ {len(results)} referensi disimpan![/]")
            else:
                print(f"✅ {len(results)} referensi disimpan!")

    elif args.command == 'cite':
        from thesis.modules.citation import CitationGenerator
        gen = CitationGenerator()
        citation = gen.from_doi(args.doi, style=args.style)
        if HAS_RICH:
            console.print(Panel(citation, title=f"Sitasi ({args.style.upper()})", border_style="green"))
        else:
            print(citation)

    elif args.command == 'manage':
        from thesis.modules.project_manager import ProjectManager
        pm = ProjectManager(db)

        if args.action == 'init':
            pm.init_default_chapters()
            if HAS_RICH:
                console.print("[green]✅ Bab 1-5 berhasil diinisialisasi![/]")
            else:
                print("✅ Bab 1-5 berhasil diinisialisasi!")

        elif args.action == 'progress':
            prog = pm.get_progress()
            if HAS_RICH:
                table = Table(title="Progress Skripsi")
                table.add_column("Bab", width=5)
                table.add_column("Judul")
                table.add_column("Status", width=10)
                table.add_column("Kata", width=15)
                table.add_column("Progress", width=10)
                for ch in prog.get('chapter_details', []):
                    bar = "█" * (ch['progress'] // 10) + "░" * (10 - ch['progress'] // 10)
                    table.add_row(str(ch['number']), ch['title'], ch['status'],
                        f"{ch['word_count']}/{ch['target_words']}", f"{bar} {ch['progress']}%")
                console.print(table)
                console.print(f"\n[bold]Total:[/] {prog.get('total_words', 0):,}/{prog.get('target_words', 0):,} kata ({prog.get('words_progress', 0)}%)")
            else:
                for ch in prog.get('chapter_details', []):
                    print(f"Bab {ch['number']}: {ch['title']} — {ch['word_count']}/{ch['target_words']} kata ({ch['progress']}%)")

        elif args.action == 'todo':
            task = ' '.join(args.args)
            if task:
                tid = pm.add_todo(task, priority=args.priority, due_date=args.due)
                print(f"✅ Todo ditambahkan: {task}")
            else:
                todos = pm.get_todos(pending_only=False)
                for t in todos:
                    mark = "✅" if t['done'] else "⬜"
                    print(f"{mark} [{t['priority']}] {t['task']}")

        elif args.action == 'chapters':
            chapters = pm.get_chapters()
            for ch in chapters:
                print(f"Bab {ch['chapter_number']}: {ch['title']} ({ch['status']}) — {ch['word_count']} kata")

    elif args.command == 'write':
        from thesis.modules.project_manager import ProjectManager
        pm = ProjectManager(db)
        chapters = pm.get_chapters()
        chapter = next((c for c in chapters if c['chapter_number'] == args.chapter), None)
        if not chapter:
            print(f"❌ Bab {args.chapter} tidak ditemukan. Jalankan: thesis-master manage init")
            return
        content = args.content
        if not content and not sys.stdin.isatty():
            content = sys.stdin.read()
        if content:
            pm.update_chapter(chapter['id'], content=content)
            print(f"✅ Bab {args.chapter} berhasil diupdate!")
        else:
            print(f"Current content of {chapter['title']}:\n")
            print(chapter.get('content', '(kosong)'))

    elif args.command == 'export':
        from thesis.modules.exporter import ThesisExporter
        exporter = ThesisExporter(db)
        meta = {'title': args.title, 'author': args.author, 'university': args.university}
        output = args.output or f'thesis.{args.format}'
        if args.format == 'docx':
            exporter.export_docx(output, meta)
        elif args.format == 'md':
            exporter.export_markdown(output, meta)
        elif args.format == 'tex':
            exporter.export_latex(output, meta)
        elif args.format == 'bib':
            exporter.export_bibtex(output)
        print(f"✅ Export berhasil: {output}")

    elif args.command == 'ai':
        from thesis.modules.ai_assistant import AIAssistant
        ai = AIAssistant()
        text = args.text
        if args.file:
            text = Path(args.file).read_text(encoding='utf-8')
        if args.action == 'summarize' and text:
            result = ai.summarize(text)
            print(result)
        elif args.action == 'paraphrase' and text:
            result = ai.paraphrase(text)
            print(result)
        elif args.action == 'review':
            from thesis.modules.reference_manager import ReferenceManager
            rm = ReferenceManager(db)
            refs = rm.list_references()
            result = ai.generate_literature_review(args.topic or 'research topic', refs[:10])
            print(result)

    elif args.command == 'serve':
        from thesis.web.app import create_app
        print(f"🚀 Thesis Master Web Dashboard")
        print(f"   http://{args.host}:{args.port}")
        app = create_app()
        app.run(host=args.host, port=args.port, debug=True)

    db.close()


if __name__ == '__main__':
    main()
