# Customizing Scoring Parameters - User Guide

This guide will help you customize how LocalMind scores your calls, even if you're not technical.

## What are Scoring Parameters?

Scoring parameters are the criteria used to evaluate call quality. Think of them as a checklist that the AI uses to grade each call. By default, LocalMind comes with 10 standard parameters, but you can:

- **Change** how important each parameter is
- **Add** your own custom parameters
- **Remove** parameters you don't need
- **Save** different sets for different purposes

## Opening the Scoring Editor

1. Launch LocalMind
2. Click **Edit** in the menu bar
3. Select **Scoring Parameters...** (or press `Ctrl+Shift+S`)

## Understanding the Interface

### Left Side - Parameter List

Shows all your parameters in a table:

- **Enabled**: Checkbox to turn parameters on/off
- **Name**: What the parameter measures
- **Category**: Type of parameter (Compliance, Quality, Communication, Custom)
- **Weight**: How important it is (shown as a colored bar)
- **Max**: Maximum points (usually 10)

### Right Side - Parameter Details

When you click a parameter on the left, you can edit:

- **Display Name**: The user-friendly name
- **Description**: What exactly this parameter measures
- **Max Score**: Maximum points (typically 10)
- **Weight**: How important this is (use the slider!)
- **Category**: Organize parameters by type
- **Enabled**: Whether to use this parameter

## How Weight Works

**Weight determines how much impact a parameter has on the final score.**

### Weight Examples

| Weight | Meaning | Visual | Use For |
|--------|---------|--------|---------|
| 0.5x | **Low** | Gray bar | Nice-to-have criteria |
| 1.0x | **Normal** | Blue bar | Standard criteria |
| 1.5x | **High** | Blue bar | Important criteria |
| 2.0x | **Critical** | Green bar | Must-have criteria |
| 3.0x | **Maximum** | Green bar | Deal-breakers |

### Using the Weight Slider

- Drag the slider left to decrease importance
- Drag the slider right to increase importance
- Or click the preset buttons: **Low**, **Normal**, **High**, **Critical**

**Tip**: Set compliance requirements (like greetings or disclosures) to 2.0x or higher!

## Creating Custom Parameters for Your Organization

### Example: Svetozar Technologies

Let's say you work for **Svetozar Technologies** and need to audit calls based on your company's specific requirements.

#### Step 1: Create a New Profile

1. Click the **New** button at the top
2. Enter a name: `Svetozar Technologies`
3. Click OK

#### Step 2: Add Your Custom Parameters

Click **Add Parameter** and create parameters specific to your needs:

**Example 1: Data Privacy Compliance**
```
Display Name: Data Privacy Compliance
Description: Agent follows GDPR and data protection protocols
Max Score: 10
Weight: 3.0x (Critical - use the slider)
Category: Compliance
Enabled: ✓
```

**Example 2: Technical Accuracy**
```
Display Name: Technical Accuracy
Description: Agent provides technically accurate product information
Max Score: 10
Weight: 2.5x (use the slider)
Category: Quality
Enabled: ✓
```

**Example 3: Brand Messaging**
```
Display Name: Brand Messaging
Description: Agent uses approved Svetozar brand messaging
Max Score: 10
Weight: 1.5x (use the slider)
Category: Communication
Enabled: ✓
```

#### Step 3: Modify Default Parameters

You might want to adjust or remove the default parameters:

- Click on "Script Compliance" in the list
- Change the weight to 2.5x (very important for your audits)
- Update the description to mention Svetozar-specific scripts

Or disable parameters you don't need:
- Click on a parameter
- Uncheck **Enabled**

#### Step 4: Save Your Profile

Click the **Save** button at the bottom. Your custom profile is now ready!

## Managing Multiple Profiles

### Why Use Multiple Profiles?

You might want different scoring criteria for:
- Different departments (Sales vs Support)
- Different products or services
- Different client requirements
- Training vs production calls

### Creating Profiles

**Option 1: Start from scratch**
1. Click **New**
2. Add your parameters one by one

**Option 2: Copy an existing profile**
1. Select the profile you want to copy
2. Click **Duplicate**
3. Give it a new name
4. Modify as needed

### Switching Profiles

Use the dropdown at the top of the editor to switch between profiles. Your current profile will be used for all future audits.

## Import/Export Profiles

### Why Import/Export?

- Share profiles with your team
- Back up your custom configurations
- Transfer profiles between computers

### Exporting a Profile

1. Select the profile you want to export
2. Click **Export**
3. Choose where to save the file (e.g., `svetozar_scoring.json`)
4. Share this file with your team

### Importing a Profile

1. Get the `.json` file from your colleague
2. Click **Import**
3. Select the file
4. The profile is now available in your dropdown

## Understanding the Summary

At the bottom of the editor, you'll see:

- **Total Weight**: Sum of all enabled parameter weights
- **Max Possible Score**: Highest score a call can achieve
- **Parameters**: How many are currently enabled

**Example Summary:**
```
Total Weight: 16.0
Max Possible Score: 160.0
Parameters: 8 enabled
```

This means:
- You have 8 parameters active
- The combined weight is 16.0x
- The maximum possible score is 160 points (which becomes 100% after normalization)

## Tips for Non-Technical Users

### 1. Start Simple
Don't try to create everything at once. Start with 4-5 key parameters that matter most to your organization.

### 2. Use Clear Descriptions
Write descriptions that anyone on your team can understand:

❌ Bad: "Adherence to protocols"
✓ Good: "Agent follows the approved greeting script and mentions the company name"

### 3. Test Your Weights
After creating a profile:
1. Process a few test calls
2. Check if the scores make sense
3. Adjust weights if needed

### 4. Group by Category
Use categories to organize:
- **Compliance**: Required steps (greetings, disclosures, data privacy)
- **Quality**: Problem-solving, accuracy, knowledge
- **Communication**: Clarity, empathy, professionalism
- **Custom**: Your organization-specific criteria

### 5. Don't Over-Engineer
You don't need 20 parameters! 6-10 well-chosen parameters are usually enough.

## Common Use Cases

### Call Center Manager
**Goal**: Ensure compliance and customer satisfaction

```
High Weight (2.0x - 3.0x):
- Script Compliance
- Problem Resolution
- Customer Satisfaction

Normal Weight (1.0x - 1.5x):
- Greeting
- Active Listening
- Call Closing
```

### Quality Assurance Team
**Goal**: Detailed analysis across many criteria

```
Critical (2.5x - 3.0x):
- Compliance with Legal Disclosures
- Data Privacy Handling

High (1.5x - 2.0x):
- Problem Identification
- Solution Accuracy
- Product Knowledge

Normal (1.0x):
- Communication Clarity
- Empathy
- Call Control
```

### Training Department
**Goal**: Identify specific areas for improvement

```
Equal Weight (1.0x for all):
- Greeting
- Active Listening
- Problem Solving
- Product Knowledge
- Communication
- Empathy
- Closing

(This gives balanced feedback on all areas)
```

## Troubleshooting

### "My changes aren't saving"
Make sure to click **Save** at the bottom before closing the editor.

### "I want to start over"
Click **Reset to Default** to restore the original 10 parameters.

### "I deleted a parameter by mistake"
If you haven't saved yet, click **Cancel** to discard changes. If you already saved, you can:
1. Select the Default profile
2. Click **Duplicate** to create a copy
3. Copy the parameter you need to your profile

### "My scores seem too high/low"
Adjust the weights! Higher weights = more impact on the final score. Try reducing weights for less critical parameters.

## Need Help?

- Click **Format Help** in the editor for JSON structure details
- Check the GitHub Issues for common questions
- Ask in GitHub Discussions

## Example: Complete Setup for Svetozar Technologies

Here's a complete example profile you could create:

| Parameter | Weight | Category | Why |
|-----------|--------|----------|-----|
| Professional Greeting | 1.5x | Compliance | Brand consistency |
| Data Privacy Compliance | 3.0x | Compliance | Legal requirement |
| Technical Accuracy | 2.5x | Quality | Product complexity |
| Problem Resolution | 2.0x | Quality | Customer satisfaction |
| Brand Messaging | 1.5x | Communication | Marketing alignment |
| Call Documentation | 1.5x | Compliance | Record keeping |

**Total Weight**: 12.0x
**Max Score**: 120 points

This profile prioritizes:
1. Legal compliance (3.0x weight)
2. Technical accuracy (2.5x weight)
3. Problem resolution (2.0x weight)

---

**Remember**: The scoring parameters are completely flexible. Customize them to match exactly what your organization needs to measure!
