""" Apple Script Tests """

import sys
from pathlib import Path
import unittest
from unittest.mock import patch, Mock

# Add the src directory to the sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from apple_script_messenger import AppleScriptMessenger  # type: ignore


class TestAppleScriptMessenger(unittest.IsolatedAsyncioTestCase):
    """Test class for AppleScriptMessenger"""

    @patch("subprocess.run")
    async def test_send_detailed_message(self, mock_subprocess_run):
        """Test sending a detailed message using AppleScriptMessenger"""

        # Arrange
        messenger = AppleScriptMessenger()
        recipient = "test@example.com"
        message = """Here's a simple yet delicious pizza recipe:

        **Classic Cheese Pizza Recipe**

        Ingredients:

        * 1 1/2 cups warm water
        * 1 tablespoon sugar
        * 2 teaspoons active dry yeast
        * 3 1/2 cups all-purpose flour
        * 1 teaspoon salt
        * 2 tablespoons olive oil
        * 1 cup pizza sauce (homemade or store-bought)
        * 8 ounces mozzarella cheese, shredded
        * Toppings of your choice (e.g., pepperoni, mushrooms, bell peppers, etc.)

        Instructions:

        1. **Make the dough:** In a large bowl, combine warm water, sugar, and yeast. Let it sit for 5-10 minutes until yeast is activated. Add flour, salt, and olive oil. Mix until a sticky ball forms.
        2. **Knead the dough:** Turn the dough onto a floured surface and knead for 5-7 minutes until smooth and elastic.
        3. **Let it rise:** Place the dough in a lightly oiled bowl, cover with plastic wrap, and let it rise in a warm place for about 1 hour, or until doubled in size.
        4. **Preheat the oven:** Preheat your oven to 425°F (220°C) with a pizza stone or baking sheet inside (optional).
        5. **Shape the dough:** Punch down the dough and shape into your desired pizza shape. Place onto a lightly floured surface or a piece of parchment paper.
        6. **Top it off:** Spread the pizza sauce evenly, leaving a small border around the edges. Top with mozzarella cheese and your favorite toppings!
        7. **Bake it:** Place the pizza on the preheated stone or baking sheet (if using) and bake for 12-15 minutes, or until crust is golden brown and cheese is melted.
        8. **Enjoy:** Remove from oven and let cool for a few minutes before slicing and serving!

        **Topping Ideas:**

        * Classic combos: pepperoni, mushrooms, bell peppers
        * Meat lovers: sausage, bacon, ham
        * Veggie delight: roasted vegetables (e.g., broccoli, cauliflower), olives, artichokes
        * Gourmet options: prosciutto, arugula, balsamic glaze

        Feel free to get creative and make it your own!"""

        mock_subprocess_run.return_value = Mock(stdout="Message sent")

        # Act
        result = await messenger.send_message_via_applescript(recipient, message)

        # Assert
        mock_subprocess_run.assert_called_once_with(
            ["osascript", "-e", messenger.get_template(), message, recipient],
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result, message)


if __name__ == "__main__":
    unittest.main()
