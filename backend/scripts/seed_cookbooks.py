"""
Database Seeding Script - Load Cookbooks and Recipes from YAML
Usage: python -m backend.scripts.seed_cookbooks
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from agents.cookbook_loader import CookbookLoader


async def seed_database():
    """
    Load all cookbooks and recipes from YAML files into PostgreSQL
    """
    print("=" * 60)
    print("COOKBOOK SEEDING SCRIPT")
    print("=" * 60)
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        loader = CookbookLoader(session)
        
        # Define cookbooks directory
        cookbooks_dir = backend_path.parent / "cookbooks"
        
        print(f"\nSearching for cookbooks in: {cookbooks_dir}")
        print(f"Directory exists: {cookbooks_dir.exists()}")
        
        # Load all cookbooks
        loaded_cookbooks = await loader.load_all_cookbooks(str(cookbooks_dir))
        
        print("\n" + "=" * 60)
        print("SEEDING COMPLETE")
        print("=" * 60)
        print(f"Total cookbooks loaded: {len(loaded_cookbooks)}")
        
        for cookbook in loaded_cookbooks:
            print(f"\n✓ {cookbook.name} v{cookbook.version}")
            print(f"  Agent Role: {cookbook.agent_role.name}")
            print(f"  Recipes: {len(cookbook.recipes)}")
            for recipe in cookbook.recipes:
                print(f"    - {recipe.name} (${recipe.cost_per_execution}/execution)")
    
    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(seed_database())
    except Exception as e:
        print(f"\n[ERROR] Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
